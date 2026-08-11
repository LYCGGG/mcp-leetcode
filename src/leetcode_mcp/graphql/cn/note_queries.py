"""GraphQL queries/mutations for notes on LeetCode CN."""

NOTE_AGGREGATE_QUERY = """
query noteAggregateNote(
    $aggregateType: AggregateNoteEnum!
    $keyword: String
    $orderBy: AggregateNoteSortingOrderEnum
    $limit: Int = 100
    $skip: Int = 0
) {
    noteAggregateNote(
        aggregateType: $aggregateType
        keyword: $keyword
        orderBy: $orderBy
        limit: $limit
        skip: $skip
    ) {
        count
        userNotes {
            id
            summary
            content
            ... on NoteAggregateQuestionNoteNode {
                noteQuestion {
                    linkTemplate
                    questionId
                    title
                    translatedTitle
                }
            }
        }
    }
}
"""

NOTE_BY_QUESTION_ID_QUERY = """
query noteOneTargetCommonNote(
    $noteType: NoteCommonTypeEnum!
    $questionId: String!
    $limit: Int = 20
    $skip: Int = 0
) {
    noteOneTargetCommonNote(
        noteType: $noteType
        targetId: $questionId
        limit: $limit
        skip: $skip
    ) {
        count
        userNotes {
            id
            summary
            content
        }
    }
}
"""

NOTE_CREATE_MUTATION = """
mutation noteCreateCommonNote(
    $content: String!
    $noteType: NoteCommonTypeEnum!
    $targetId: String!
    $summary: String!
) {
    noteCreateCommonNote(
        content: $content
        noteType: $noteType
        targetId: $targetId
        summary: $summary
    ) {
        note {
            id
            content
            targetId
        }
        ok
    }
}
"""

NOTE_UPDATE_MUTATION = """
mutation noteUpdateUserNote(
    $content: String!
    $noteId: ID!
    $summary: String!
) {
    noteUpdateUserNote(content: $content, noteId: $noteId, summary: $summary) {
        note {
            id
            content
            targetId
        }
        ok
    }
}
"""
