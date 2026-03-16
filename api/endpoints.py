class Endpoints:
    """
    All URL-paths from apimocker.com
    """

    # Users
    USERS = "/users"
    USER_BY_ID = "/users/{user_id}"

    # Posts
    POSTS = "/posts"
    POST_BY_ID = "/posts/{post_id}"

    # Todos
    TODOS = "/todos"
    TODO_BY_ID = "/todos/{todo_id}"

    # Comments
    COMMENTS = "/comments"
    COMMENT_BY_ID = "/comments/{comment_id}"

    @staticmethod
    def user(user_id: int | str) -> str:
        return Endpoints.USER_BY_ID.format(user_id=user_id)

    @staticmethod
    def post(post_id: int | str) -> str:
        return Endpoints.POST_BY_ID.format(post_id=post_id)

    @staticmethod
    def todo(todo_id: int | str) -> str:
        return Endpoints.TODO_BY_ID.format(todo_id=todo_id)

    @staticmethod
    def comment(comment_id: int | str) -> str:
        return Endpoints.COMMENT_BY_ID.format(comment_id=comment_id)
