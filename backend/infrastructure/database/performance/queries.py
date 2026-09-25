def explain_query(queryset) -> str:
    """Return a non-mutating PostgreSQL execution plan for a QuerySet."""
    return queryset.explain(analyze=False, verbose=True, buffers=True)
