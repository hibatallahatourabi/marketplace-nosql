
def benchmark_query(db, collection_name, filter_query, index_name=None):

    explain_command = {
        "explain": {
            "find": collection_name,
            "filter": filter_query
        },
        "verbosity": "executionStats"
    }

    if index_name:
        explain_command["explain"]["hint"] = index_name

    result = db.command(explain_command)

    stats = result["executionStats"]

    return {
        "execution_time_ms": stats["executionTimeMillis"],
        "documents_examined": stats["totalDocsExamined"],
        "documents_returned": stats["nReturned"],
        "winning_plan": result["queryPlanner"]["winningPlan"]
    }
