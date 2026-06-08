import re

from atguigu.domain.messages import FocusedObject


class FocusedObjectTextSwitch:
    """
    功能：在纯文本里寻找唯一对象命中，用于切换 focused object。
    """

    def match_candidate_from_text(
        self,
        *,
        text: str | None,
        candidates: list[FocusedObject],
        current_object: FocusedObject | None,
    ) -> FocusedObject | None:
        """
        功能：从文本中匹配唯一候选对象，用于切换 focused object。

        输入：
        - text: 当前用户文本。
        - candidates: 当前住户所有候选对象。
        - current_object: 当前已聚焦对象，可为空。

        输出：
        - FocusedObject | None: 命中唯一候选时返回对象，否则返回 None。

        调用情况：
        - `FocusedObjectResolver.try_switch_focused_object_from_text()`

        副作用：
        - 无。
        """
        normalized_text = self.normalize_match_text(text)
        if not normalized_text:
            return None

        # 优先级依次为：ID 精确命中、标题全匹配、标题被文本包含。
        for matcher in (
            self._match_unique_id_candidate,
            self._match_unique_exact_title_candidate,
            self._match_unique_title_contains_candidate,
        ):
            matched = matcher(
                normalized_text=normalized_text,
                candidates=candidates,
                current_object=current_object,
            )
            if matched is not None:
                return matched

        return None

    @staticmethod
    def _is_current_object(
        candidate: FocusedObject,
        current_object: FocusedObject | None,
    ) -> bool:
        """
        功能：判断候选对象是否就是当前已聚焦对象。

        输入：
        - candidate: 当前候选对象。
        - current_object: 当前已聚焦对象。

        输出：
        - bool: 同类型且 ID 相同时返回 True。

        调用情况：
        - 各匹配分支的去重逻辑。

        副作用：
        - 无。
        """
        return (
            current_object is not None
            and candidate.type == current_object.type
            and candidate.id == current_object.id
        )

    def _match_unique_id_candidate(
        self,
        *,
        normalized_text: str,
        candidates: list[FocusedObject],
        current_object: FocusedObject | None,
    ) -> FocusedObject | None:
        """
        功能：按对象 ID 在文本中匹配唯一候选对象。

        输入：
        - normalized_text: 标准化后的用户文本。
        - candidates: 候选对象列表。
        - current_object: 当前已聚焦对象。

        输出：
        - FocusedObject | None: 命中唯一候选时返回对象，否则返回 None。

        调用情况：
        - `match_candidate_from_text()`

        副作用：
        - 无。
        """
        return self._find_unique_candidate(
            candidates=candidates,
            current_object=current_object,
            matcher=lambda candidate: self._matches_candidate_id(candidate, normalized_text),
        )

    def _match_unique_exact_title_candidate(
        self,
        *,
        normalized_text: str,
        candidates: list[FocusedObject],
        current_object: FocusedObject | None,
    ) -> FocusedObject | None:
        """
        功能：按对象标题全量匹配唯一候选对象。

        输入：
        - normalized_text: 标准化后的用户文本。
        - candidates: 候选对象列表。
        - current_object: 当前已聚焦对象。

        输出：
        - FocusedObject | None: 命中唯一候选时返回对象，否则返回 None。

        调用情况：
        - `match_candidate_from_text()`

        副作用：
        - 无。
        """
        return self._find_unique_candidate(
            candidates=candidates,
            current_object=current_object,
            matcher=lambda candidate: self._matches_candidate_exact_title(candidate, normalized_text),
        )

    def _match_unique_title_contains_candidate(
        self,
        *,
        normalized_text: str,
        candidates: list[FocusedObject],
        current_object: FocusedObject | None,
    ) -> FocusedObject | None:
        """
        功能：按“标题被文本包含”规则匹配唯一候选对象。

        输入：
        - normalized_text: 标准化后的用户文本。
        - candidates: 候选对象列表。
        - current_object: 当前已聚焦对象。

        输出：
        - FocusedObject | None: 命中唯一候选时返回对象，否则返回 None。

        调用情况：
        - `match_candidate_from_text()`

        副作用：
        - 无。
        """
        return self._find_unique_candidate(
            candidates=candidates,
            current_object=current_object,
            matcher=lambda candidate: self._matches_candidate_title_contains(
                candidate=candidate,
                normalized_text=normalized_text,
                current_object=current_object,
            ),
        )

    def _find_unique_candidate(
        self,
        *,
        candidates: list[FocusedObject],
        current_object: FocusedObject | None,
        matcher,
    ) -> FocusedObject | None:
        """
        功能：在候选列表中筛出满足 matcher 的唯一对象。

        输入：
        - candidates: 候选对象列表。
        - current_object: 当前已聚焦对象。
        - matcher: 用于判断候选是否命中的匹配函数。

        输出：
        - FocusedObject | None: 只有命中结果唯一时才返回对象。

        调用情况：
        - 三种具体匹配策略复用。

        副作用：
        - 无。
        """
        matched_candidates = [
            candidate
            for candidate in candidates
            if not self._is_current_object(candidate, current_object) and matcher(candidate)
        ]
        if len(matched_candidates) == 1:
            return matched_candidates[0]
        return None

    def _matches_candidate_id(
        self,
        candidate: FocusedObject,
        normalized_text: str,
    ) -> bool:
        """
        功能：判断文本中是否包含候选对象 ID。

        输入：
        - candidate: 候选对象。
        - normalized_text: 标准化后的用户文本。

        输出：
        - bool: 文本包含候选 ID 时返回 True。

        调用情况：
        - `_match_unique_id_candidate()`

        副作用：
        - 无。
        """
        normalized_id = self.normalize_match_text(candidate.id)
        return bool(normalized_id and normalized_id in normalized_text)

    def _matches_candidate_exact_title(
        self,
        candidate: FocusedObject,
        normalized_text: str,
    ) -> bool:
        """
        功能：判断文本是否与候选对象标题完全一致。

        输入：
        - candidate: 候选对象。
        - normalized_text: 标准化后的用户文本。

        输出：
        - bool: 标题全匹配时返回 True。

        调用情况：
        - `_match_unique_exact_title_candidate()`

        副作用：
        - 无。
        """
        normalized_title = self.normalize_match_text(candidate.title)
        return bool(normalized_title and normalized_title == normalized_text)

    def _matches_candidate_title_contains(
        self,
        *,
        candidate: FocusedObject,
        normalized_text: str,
        current_object: FocusedObject | None,
    ) -> bool:
        """
        功能：判断候选标题是否被当前文本包含，并满足对象类型约束。

        输入：
        - candidate: 候选对象。
        - normalized_text: 标准化后的用户文本。
        - current_object: 当前已聚焦对象。

        输出：
        - bool: 符合“标题包含”匹配规则时返回 True。

        调用情况：
        - `_match_unique_title_contains_candidate()`

        副作用：
        - 无。
        """
        normalized_title = self.normalize_match_text(candidate.title)
        if not normalized_title or normalized_title not in normalized_text:
            return False
        if current_object is not None and current_object.type != candidate.type:
            return False
        return True

    @staticmethod
    def normalize_match_text(text: str | None) -> str:
        """
        功能：做对象文本匹配前的标准化清洗。

        输入：
        - text: 原始文本。

        输出：
        - str: 去掉空白、常见标点并转小写后的文本。

        调用情况：
        - 所有匹配分支复用。

        副作用：
        - 无。
        """
        normalized = (text or "").strip().lower()
        return re.sub(r"[\s,，。？！、\[\]（）()\"'~\-]+", "", normalized)
