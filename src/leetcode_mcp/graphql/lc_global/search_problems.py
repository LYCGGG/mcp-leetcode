"""GraphQL query for searching problems on LeetCode Global.

Uses aliases to normalize the response shape to match CN.
"""

SEARCH_PROBLEMS_QUERY = """
query (
    $categorySlug: String
    $limit: Int
    $skip: Int
    $filters: QuestionListFilterInput
) {
    problemsetQuestionList: questionList(
        categorySlug: $categorySlug
        limit: $limit
        skip: $skip
        filters: $filters
    ) {
        total: totalNum
        questions: data {
            acRate
            difficulty
            title
            titleSlug
            topicTags {
                slug
            }
        }
    }
}
"""
