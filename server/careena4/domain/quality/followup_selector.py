from careena4.models.domain import FollowupNeed


class FollowupSelector:
    _PRIORITY_SCORE = {"high": 3, "medium": 2, "low": 1}

    def select(self, *, followup_needs: list[FollowupNeed]) -> FollowupNeed | None:
        open_needs = [need for need in followup_needs if not need.resolved]
        if not open_needs:
            return None
        return max(open_needs, key=lambda need: (int(need.blocking), self._PRIORITY_SCORE[need.priority]))
