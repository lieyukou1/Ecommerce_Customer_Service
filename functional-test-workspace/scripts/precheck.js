async function tryFetchJson(url, options = {}) {
  try {
    const response = await fetch(url, options);
    const contentType = response.headers.get("content-type") || "";
    const body = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    return {
      ok: response.ok,
      status: response.status,
      body,
    };
  } catch (error) {
    return {
      ok: false,
      status: null,
      body: null,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

export async function runPrecheck(config) {
  const residentId = config.defaultResidentId;
  const checks = [];

  checks.push({
    id: "frontend-home",
    title: "Frontend home page",
    target: config.frontendBaseUrl,
    ...(await tryFetchJson(config.frontendBaseUrl)),
  });

  checks.push({
    id: "assistant-chat",
    title: "Local assistant /api/chat",
    target: `${config.localAssistantBaseUrl}/api/chat`,
    ...(await tryFetchJson(`${config.localAssistantBaseUrl}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        resident_id: residentId,
        text: "预检消息",
      }),
    })),
  });

  checks.push({
    id: "assistant-history",
    title: "Local assistant /api/chat/history",
    target: `${config.localAssistantBaseUrl}/api/chat/history?resident_id=${residentId}`,
    ...(await tryFetchJson(
      `${config.localAssistantBaseUrl}/api/chat/history?resident_id=${residentId}`,
    )),
  });

  checks.push({
    id: "assistant-state",
    title: "Local assistant /api/chat/state",
    target: `${config.localAssistantBaseUrl}/api/chat/state?resident_id=${residentId}`,
    ...(await tryFetchJson(
      `${config.localAssistantBaseUrl}/api/chat/state?resident_id=${residentId}`,
    )),
  });

  if (config.skipPropertyBackendPrecheck) {
    checks.push({
      id: "property-work-orders",
      title: "Property backend work-order list",
      target: `${config.propertyBackendBaseUrl}/residents/${residentId}/work-orders`,
      ok: true,
      skipped: true,
      status: null,
      body: "Skipped by SKIP_PROPERTY_BACKEND_PRECHECK=1",
    });

    checks.push({
      id: "property-service-items",
      title: "Property backend service-item list",
      target: `${config.propertyBackendBaseUrl}/residents/${residentId}/service-items`,
      ok: true,
      skipped: true,
      status: null,
      body: "Skipped by SKIP_PROPERTY_BACKEND_PRECHECK=1",
    });
  } else {
    checks.push({
      id: "property-work-orders",
      title: "Property backend work-order list",
      target: `${config.propertyBackendBaseUrl}/residents/${residentId}/work-orders`,
      ...(await tryFetchJson(`${config.propertyBackendBaseUrl}/residents/${residentId}/work-orders`)),
    });

    checks.push({
      id: "property-service-items",
      title: "Property backend service-item list",
      target: `${config.propertyBackendBaseUrl}/residents/${residentId}/service-items`,
      ...(await tryFetchJson(`${config.propertyBackendBaseUrl}/residents/${residentId}/service-items`)),
    });
  }

  const hasFailure = checks.some((check) => !check.ok);

  return {
    ok: !hasFailure,
    checks,
  };
}
