class SelfRouter:

    def route(self, query):

        q = query.lower()

        # Vision model queries
        if any(word in q for word in [
            "image",
            "picture",
            "photo",
            "diagram",
            "graph",
            "chart"
        ]):
            return "vlm"

        # Reasoning queries
        if any(word in q for word in [
            "compare",
            "difference",
            "analyze",
            "step by step",
            "why"
        ]):
            return "reasoning"

        if len(query.split()) > 25:
            return "reasoning"

        # Default
        return "llm"