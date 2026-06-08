import {
  classifyScenarioResult,
  extractBotTexts,
  summarizeMessages,
} from "./utils.js";

function safeParseJson(text) {
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return { _raw: text };
  }
}

async function requestJson(url, options = {}) {
  try {
    const response = await fetch(url, options);
    const rawText = await response.text();
    return {
      statusCode: response.status,
      data: safeParseJson(rawText),
      error: null,
    };
  } catch (error) {
    return {
      statusCode: null,
      data: null,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

async function postChat(baseUrl, residentId, payload) {
  const requestBody = {
    resident_id: residentId,
    ...payload,
  };

  const response = await requestJson(`${baseUrl}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestBody),
  });

  return {
    requestBody,
    ...response,
  };
}

async function fetchStateSnapshot(baseUrl, residentId) {
  return requestJson(`${baseUrl}/api/chat/state?resident_id=${encodeURIComponent(residentId)}`);
}

async function resetStateSnapshot(baseUrl, residentId) {
  return requestJson(`${baseUrl}/api/chat/state?resident_id=${encodeURIComponent(residentId)}`, {
    method: "DELETE",
  });
}

async function seedStateSnapshot(baseUrl, residentId, state) {
  return requestJson(`${baseUrl}/api/chat/state`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      resident_id: residentId,
      state,
    }),
  });
}

function normalizeState(rawState) {
  const state = rawState || {};
  return {
    resident_id: state.resident_id || null,
    active_task: state.active_task || null,
    paused_tasks: Array.isArray(state.paused_tasks) ? state.paused_tasks : [],
    active_system_task: state.active_system_task || null,
    focused_object: state.focused_object || null,
    conversation_state: state.conversation_state || null,
    last_transition: state.last_transition || null,
    last_route: state.last_route || null,
    last_task_outcome: state.last_task_outcome || null,
    sessions: Array.isArray(state.sessions) ? state.sessions : [],
    current_session_id: state.current_session_id || null,
  };
}

function getByPath(target, path) {
  if (!path) {
    return target;
  }

  return path.split(".").reduce((current, segment) => {
    if (current === null || current === undefined) {
      return undefined;
    }
    return current[segment];
  }, target);
}

function valuesEqual(left, right) {
  return JSON.stringify(left) === JSON.stringify(right);
}

function inferTrack({ state, messages }) {
  const explicitRoute = state.last_route?.kind;
  if (explicitRoute === "task" || explicitRoute === "knowledge" || explicitRoute === "clarify" || explicitRoute === "chitchat") {
    return explicitRoute;
  }

  if (state.active_task) {
    return "task";
  }
  if (state.active_system_task && state.active_system_task.flow_id !== "system_collect_information") {
    return "task";
  }

  const explicitState = state.conversation_state;
  if (explicitState === "active_task" || explicitState === "transitioning") {
    return "task";
  }
  if (explicitState === "clarifying") {
    return "clarify";
  }
  if (explicitState === "focused_knowledge") {
    return "knowledge";
  }
  if (explicitState === "chitchat" || explicitState === "idle") {
    return "chitchat";
  }

  const joinedText = extractBotTexts(messages).join("\n");

  if (state.active_task || state.active_system_task) {
    return "task";
  }

  if (state.focused_object) {
    if (
      joinedText.includes("还是") ||
      joinedText.includes("想了解") ||
      joinedText.includes("请先") ||
      joinedText.includes("你是想")
    ) {
      return "clarify";
    }
    return "knowledge";
  }

  if (
    joinedText.includes("还是") ||
    joinedText.includes("请问") ||
    joinedText.includes("你是想")
  ) {
    return "clarify";
  }

  return "chitchat";
}

function buildFocusedObjectSummary(focusedObject) {
  if (!focusedObject) {
    return null;
  }

  return {
    type: focusedObject.type || null,
    id: focusedObject.id || null,
    title: focusedObject.title || null,
  };
}

function assertMessageTexts(messages, checkpoint, assertionErrors) {
  const joinedText = extractBotTexts(messages).join("\n");

  for (const phrase of checkpoint.message_includes_all || []) {
    if (!joinedText.includes(phrase)) {
      assertionErrors.push(`bot message did not include required phrase: ${phrase}`);
    }
  }

  const includesAny = checkpoint.message_includes_any || [];
  if (includesAny.length > 0 && !includesAny.some((phrase) => joinedText.includes(phrase))) {
    assertionErrors.push(`bot message did not include any expected phrase: ${includesAny.join(", ")}`);
  }

  for (const phrase of checkpoint.message_excludes || []) {
    if (joinedText.includes(phrase)) {
      assertionErrors.push(`bot message included forbidden phrase: ${phrase}`);
    }
  }
}

function assertStateSnapshot(state, checkpoint, assertionErrors) {
  if (Object.prototype.hasOwnProperty.call(checkpoint, "focused_object")) {
    const expected = checkpoint.focused_object;
    const actual = buildFocusedObjectSummary(state.focused_object);
    if (!valuesEqual(actual, expected)) {
      assertionErrors.push(
        `focused_object mismatch: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`,
      );
    }
  }

  const focusedObjectAnyOf = checkpoint.focused_object_any_of || [];
  if (focusedObjectAnyOf.length > 0) {
    const actual = buildFocusedObjectSummary(state.focused_object);
    const matched = focusedObjectAnyOf.some((expected) => valuesEqual(actual, expected));
    if (!matched) {
      assertionErrors.push(
        `focused_object did not match any expected candidate: ${JSON.stringify(focusedObjectAnyOf)}`,
      );
    }
  }

  for (const forbiddenId of checkpoint.forbidden_focused_object_ids || []) {
    if (state.focused_object?.id === forbiddenId) {
      assertionErrors.push(`focused_object should not remain on forbidden id: ${forbiddenId}`);
    }
  }

  if (Object.prototype.hasOwnProperty.call(checkpoint, "active_task_flow_id")) {
    const actualFlowId = state.active_task?.flow_id || null;
    if (actualFlowId !== checkpoint.active_task_flow_id) {
      assertionErrors.push(
        `active_task.flow_id mismatch: expected ${checkpoint.active_task_flow_id}, got ${actualFlowId}`,
      );
    }
  }

  if (Object.prototype.hasOwnProperty.call(checkpoint, "active_task_step_id")) {
    const actualStepId = state.active_task?.step_id || null;
    if (actualStepId !== checkpoint.active_task_step_id) {
      assertionErrors.push(
        `active_task.step_id mismatch: expected ${checkpoint.active_task_step_id}, got ${actualStepId}`,
      );
    }
  }

  if (Object.prototype.hasOwnProperty.call(checkpoint, "paused_task_count")) {
    const actualCount = state.paused_tasks.length;
    if (actualCount !== checkpoint.paused_task_count) {
      assertionErrors.push(
        `paused_tasks count mismatch: expected ${checkpoint.paused_task_count}, got ${actualCount}`,
      );
    }
  }

  if (Object.prototype.hasOwnProperty.call(checkpoint, "paused_task_flow_ids")) {
    const actualFlowIds = state.paused_tasks.map((task) => task.flow_id);
    if (!valuesEqual(actualFlowIds, checkpoint.paused_task_flow_ids)) {
      assertionErrors.push(
        `paused_task_flow_ids mismatch: expected ${JSON.stringify(checkpoint.paused_task_flow_ids)}, got ${JSON.stringify(actualFlowIds)}`,
      );
    }
  }

  if (Object.prototype.hasOwnProperty.call(checkpoint, "active_system_task_flow_id")) {
    const actualFlowId = state.active_system_task?.flow_id || null;
    if (actualFlowId !== checkpoint.active_system_task_flow_id) {
      assertionErrors.push(
        `active_system_task.flow_id mismatch: expected ${checkpoint.active_system_task_flow_id}, got ${actualFlowId}`,
      );
    }
  }

  const expectedTaskOutcomeKinds = checkpoint.expected_task_outcome_kinds || [];
  if (expectedTaskOutcomeKinds.length > 0) {
    const actualKind = state.last_task_outcome?.kind || null;
    if (!expectedTaskOutcomeKinds.includes(actualKind)) {
      assertionErrors.push(
        `last_task_outcome.kind mismatch: expected one of ${JSON.stringify(expectedTaskOutcomeKinds)}, got ${actualKind}`,
      );
    }
  } else if (Object.prototype.hasOwnProperty.call(checkpoint, "expected_task_outcome_kind")) {
    const actualKind = state.last_task_outcome?.kind || null;
    if (actualKind !== checkpoint.expected_task_outcome_kind) {
      assertionErrors.push(
        `last_task_outcome.kind mismatch: expected ${checkpoint.expected_task_outcome_kind}, got ${actualKind}`,
      );
    }
  }

  if (Object.prototype.hasOwnProperty.call(checkpoint, "expected_task_outcome_flow_id")) {
    const actualFlowId = state.last_task_outcome?.flow_id || null;
    if (actualFlowId !== checkpoint.expected_task_outcome_flow_id) {
      assertionErrors.push(
        `last_task_outcome.flow_id mismatch: expected ${checkpoint.expected_task_outcome_flow_id}, got ${actualFlowId}`,
      );
    }
  }

  const taskOutcomeReasonIncludes = checkpoint.task_outcome_reason_includes || [];
  if (taskOutcomeReasonIncludes.length > 0) {
    const actualReason = state.last_task_outcome?.reason || "";
    for (const phrase of taskOutcomeReasonIncludes) {
      if (!actualReason.includes(phrase)) {
        assertionErrors.push(
          `last_task_outcome.reason did not include required phrase: ${phrase}`,
        );
      }
    }
  }

  for (const forbiddenFlowId of checkpoint.forbidden_flow_ids || []) {
    if (state.active_task?.flow_id === forbiddenFlowId) {
      assertionErrors.push(`active_task hit forbidden flow: ${forbiddenFlowId}`);
    }
    if (state.active_system_task?.flow_id === forbiddenFlowId) {
      assertionErrors.push(`active_system_task hit forbidden flow: ${forbiddenFlowId}`);
    }
    if (state.paused_tasks.some((task) => task.flow_id === forbiddenFlowId)) {
      assertionErrors.push(`paused_tasks still contains forbidden flow: ${forbiddenFlowId}`);
    }
  }

  for (const [path, expectedValue] of Object.entries(checkpoint.state_paths || {})) {
    const actualValue = getByPath(state, path);
    if (!valuesEqual(actualValue, expectedValue)) {
      assertionErrors.push(
        `state path mismatch at ${path}: expected ${JSON.stringify(expectedValue)}, got ${JSON.stringify(actualValue)}`,
      );
    }
  }
}

function evaluateCheckpoint({ state, messages, checkpoint }) {
  const assertionErrors = [];
  const inferredTrack = inferTrack({ state, messages });

  const expectedTracks = checkpoint.expected_tracks || [];
  if (expectedTracks.length > 0) {
    if (!expectedTracks.includes(inferredTrack)) {
      assertionErrors.push(
        `track mismatch: expected one of ${JSON.stringify(expectedTracks)}, got ${inferredTrack}`,
      );
    }
  } else if (checkpoint.expected_track && checkpoint.expected_track !== inferredTrack) {
    assertionErrors.push(
      `track mismatch: expected ${checkpoint.expected_track}, got ${inferredTrack}`,
    );
  }

  assertStateSnapshot(state, checkpoint, assertionErrors);
  assertMessageTexts(messages, checkpoint, assertionErrors);

  return {
    inferredTrack,
    assertionErrors,
  };
}

function buildTurnPayload(turn) {
  if (turn.payload) {
    return turn.payload;
  }

  const payload = {};
  if (turn.text) {
    payload.text = turn.text;
  }
  if (turn.object) {
    payload.object = turn.object;
  }
  return payload;
}

function summarizeState(state) {
  return {
    conversation_state: state.conversation_state,
    last_transition: state.last_transition,
    last_route: state.last_route,
    last_task_outcome: state.last_task_outcome,
    focused_object: buildFocusedObjectSummary(state.focused_object),
    active_task: state.active_task
      ? {
          flow_id: state.active_task.flow_id || null,
          step_id: state.active_task.step_id || null,
          slots: state.active_task.slots || {},
        }
      : null,
    paused_tasks: state.paused_tasks.map((task) => ({
      flow_id: task.flow_id || null,
      step_id: task.step_id || null,
      slots: task.slots || {},
    })),
    active_system_task: state.active_system_task
      ? {
          flow_id: state.active_system_task.flow_id || null,
          step_id: state.active_system_task.step_id || null,
        }
      : null,
    current_session_id: state.current_session_id,
    session_count: state.sessions.length,
  };
}

function aggregateScenarioResult(turnLogs, finalAssertionErrors) {
  const results = turnLogs.map((turnLog) => turnLog.result);

  if (results.includes("infra_fail")) {
    return "infra_fail";
  }

  if (results.includes("behavior_fail") || finalAssertionErrors.length > 0) {
    return "behavior_fail";
  }

  if (results.includes("placeholder_pass")) {
    return "placeholder_pass";
  }

  return "pass";
}

async function prepareScenarioState(baseUrl, scenario) {
  const resetResponse = await resetStateSnapshot(baseUrl, scenario.residentId);
  if (resetResponse.error || (resetResponse.statusCode && resetResponse.statusCode >= 400)) {
    return {
      ok: false,
      action: "reset",
      response: resetResponse,
    };
  }

  if (!scenario.seed_state) {
    return {
      ok: true,
      action: "reset",
      response: resetResponse,
    };
  }

  const seedResponse = await seedStateSnapshot(baseUrl, scenario.residentId, scenario.seed_state);
  return {
    ok: !seedResponse.error && (!seedResponse.statusCode || seedResponse.statusCode < 400),
    action: "seed",
    response: seedResponse,
  };
}

export async function runApiScenarios({ config, scenarios, breakpointController }) {
  const scenarioLogs = [];

  for (const scenario of scenarios) {
    const preparation = await prepareScenarioState(config.localAssistantBaseUrl, scenario);
    const turnLogs = [];

    if (!preparation.ok) {
      scenarioLogs.push({
        scenario,
        result: "infra_fail",
        preparation,
        turns: [],
        final_assertions: [],
      });
      continue;
    }

    for (const turn of scenario.turns) {
      const responseInfo = await postChat(
        config.localAssistantBaseUrl,
        scenario.residentId,
        buildTurnPayload(turn),
      );

      const messages = Array.isArray(responseInfo.data?.messages) ? responseInfo.data.messages : [];
      const stateResponse = await fetchStateSnapshot(config.localAssistantBaseUrl, scenario.residentId);
      const state = normalizeState(stateResponse.data?.state);

      const checkpoint = turn.checkpoint || {};
      const { inferredTrack, assertionErrors } = evaluateCheckpoint({
        state,
        messages,
        checkpoint,
      });

      if (stateResponse.error) {
        assertionErrors.push(`state snapshot error: ${stateResponse.error}`);
      } else if (stateResponse.statusCode && stateResponse.statusCode >= 400) {
        assertionErrors.push(`state snapshot HTTP ${stateResponse.statusCode}`);
      }

      const verdict = classifyScenarioResult({
        statusCode: responseInfo.statusCode,
        error: responseInfo.error,
        messages,
        assertionErrors,
      });

      const turnLog = {
        scenario_id: scenario.id,
        step_id: turn.id,
        channel: "api-regression",
        track: inferredTrack,
        tags: scenario.tags || [],
        request: {
          target: `${config.localAssistantBaseUrl}/api/chat`,
          body: responseInfo.requestBody,
        },
        response: {
          status: responseInfo.statusCode,
          body: responseInfo.data,
          error: responseInfo.error || null,
        },
        state_snapshot: summarizeState(state),
        state_snapshot_raw: stateResponse.data?.state || null,
        result: verdict.result,
        reason: verdict.reason,
        assertion_errors: assertionErrors,
        bot_message_summary: summarizeMessages(messages),
      };

      turnLogs.push(turnLog);
      await breakpointController.pause(`${scenario.id}/${turn.id}`, turnLog);
    }

    const finalStateResponse = await fetchStateSnapshot(
      config.localAssistantBaseUrl,
      scenario.residentId,
    );
    const finalState = normalizeState(finalStateResponse.data?.state);
    const finalMessages =
      turnLogs.length > 0
        ? turnLogs[turnLogs.length - 1].response.body?.messages || []
        : [];
    const finalCheckpoint = scenario.final_assertions || {};
    const finalEvaluation = evaluateCheckpoint({
      state: finalState,
      messages: finalMessages,
      checkpoint: finalCheckpoint,
    });
    const finalAssertionErrors = [...finalEvaluation.assertionErrors];

    if (finalStateResponse.error) {
      finalAssertionErrors.push(`final state snapshot error: ${finalStateResponse.error}`);
    } else if (finalStateResponse.statusCode && finalStateResponse.statusCode >= 400) {
      finalAssertionErrors.push(`final state snapshot HTTP ${finalStateResponse.statusCode}`);
    }

    scenarioLogs.push({
      scenario,
      result: aggregateScenarioResult(turnLogs, finalAssertionErrors),
      preparation,
      turns: turnLogs,
      final_assertions: finalAssertionErrors,
      final_track: finalEvaluation.inferredTrack,
      final_state_snapshot: summarizeState(finalState),
    });
  }

  return scenarioLogs;
}
