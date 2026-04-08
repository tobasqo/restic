# ruff: noqa: INP001
import asyncio
import logging
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from pydantic.alias_generators import to_camel

from restic import ResticClient
from restic.routes.common import CrudRoutes
from restic.routes.mixins import ListMixin

BASE_URL = "https://jsonplaceholder.typicode.com/"

TResultModel = TypeVar("TResultModel", bound=BaseModel)
TListResultModel = TypeVar("TListResultModel", bound=BaseModel)


class JSONPlaceholderBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        extra="forbid",
    )


class ListResult(JSONPlaceholderBaseModel, Generic[TResultModel]):
    results: list[TResultModel]


class JSONPlaceholderListMixin(ListMixin):
    # noinspection PyMethodMayBeStatic
    def _validate_list_result_model(
        self,
        response_data: Any,
        result_model_type: type[TListResultModel],
    ) -> TListResultModel:
        return result_model_type.model_validate({"results": response_data})


class PostId(JSONPlaceholderBaseModel):
    id: int


class Post(PostId):
    user_id: int
    title: str
    body: str


class PostQueryParams(JSONPlaceholderBaseModel):
    id: int | None = None
    user_id: int | None = None
    title: str | None = None
    body: str | None = None


class PostCreate(JSONPlaceholderBaseModel):
    user_id: int
    title: str
    body: str


class PostUpdate(PostId):
    user_id: int
    title: str
    body: str


class PostPartialUpdate(JSONPlaceholderBaseModel):
    id: int | None = None
    user_id: int | None = None
    title: str | None = None
    body: str | None = None


class CommentId(JSONPlaceholderBaseModel):
    id: int


class Comment(CommentId):
    id: int
    post_id: int
    name: str
    email: str
    body: str


class CommentQueryParams(JSONPlaceholderBaseModel):
    id: int | None = None
    post_id: int | None = None
    name: str | None = None
    email: str | None = None
    body: str | None = None


class CommentCreate(JSONPlaceholderBaseModel):
    post_id: int
    name: str
    email: str
    body: str


class CommentUpdate(JSONPlaceholderBaseModel):
    id: int
    post_id: int
    name: str
    email: str
    body: str


class CommentPartialUpdate(JSONPlaceholderBaseModel):
    id: int | None = None
    post_id: int | None = None
    name: str | None = None
    email: str | None = None
    body: str | None = None


class AlbumId(JSONPlaceholderBaseModel):
    id: int


class Album(AlbumId):
    user_id: int
    title: str


class AlbumQueryParams(JSONPlaceholderBaseModel):
    id: int | None = None
    user_id: int | None = None
    title: str | None = None


class AlbumCreate(JSONPlaceholderBaseModel):
    user_id: int
    title: str


class AlbumUpdate(JSONPlaceholderBaseModel):
    id: int
    user_id: int
    title: str


class AlbumPartialUpdate(JSONPlaceholderBaseModel):
    id: int | None = None
    user_id: int | None = None
    title: str | None = None


class PhotoId(JSONPlaceholderBaseModel):
    id: int


class Photo(PhotoId):
    album_id: int
    title: str
    url: HttpUrl
    thumbnail_url: HttpUrl


class PhotoQueryParams(JSONPlaceholderBaseModel):
    id: int | None = None
    album_id: int | None = None
    title: str | None = None
    url: HttpUrl | None = None
    thumbnail_url: HttpUrl | None = None


class PhotoCreate(JSONPlaceholderBaseModel):
    album_id: int
    title: str
    url: HttpUrl
    thumbnail_url: HttpUrl


class PhotoUpdate(JSONPlaceholderBaseModel):
    album_id: int
    title: str
    url: HttpUrl
    thumbnail_url: HttpUrl


class PhotoPartialUpdate(JSONPlaceholderBaseModel):
    id: int | None = None
    album_id: int | None = None
    title: str | None = None
    url: HttpUrl | None = None
    thumbnail_url: HttpUrl | None = None


class TodoId(JSONPlaceholderBaseModel):
    id: int


class Todo(TodoId):
    user_id: int
    title: str
    completed: bool = False


class TodoQueryParams(JSONPlaceholderBaseModel):
    id: int | None = None
    user_id: int | None = None
    title: str | None = None
    completed: bool | None = None


class TodoCreate(JSONPlaceholderBaseModel):
    user_id: int
    title: str
    completed: bool = False


class TodoUpdate(JSONPlaceholderBaseModel):
    id: int
    user_id: int
    title: str
    completed: bool = False


class TodoPartialUpdate(JSONPlaceholderBaseModel):
    id: int | None = None
    user_id: int | None = None
    title: str | None = None
    completed: bool | None = None


class Geolocation(JSONPlaceholderBaseModel):
    latitude: float = Field(alias="lat")
    longitude: float = Field(alias="lng")


class Company(JSONPlaceholderBaseModel):
    name: str
    catch_phrase: str
    bs: str


class Address(JSONPlaceholderBaseModel):
    street: str
    suite: str
    city: str
    zipcode: str
    geo: Geolocation


class UserId(JSONPlaceholderBaseModel):
    id: int


class User(UserId):
    name: str
    username: str
    email: str
    address: Address
    phone: str
    website: str
    company: Company


class UserQueryParams(JSONPlaceholderBaseModel):
    id: int | None = None
    name: str | None = None
    username: str | None = None
    phone: str | None = None
    website: str | None = None


class UserCreate(JSONPlaceholderBaseModel):
    name: str
    username: str
    email: str
    address: Address
    phone: str
    website: str
    company: Company


class UserUpdate(JSONPlaceholderBaseModel):
    id: int
    name: str
    username: str
    email: str
    address: Address
    phone: str
    website: str
    company: Company


class UserPartialUpdate(JSONPlaceholderBaseModel):
    id: int | None = None
    name: str | None = None
    username: str | None = None
    email: str | None = None
    address: Address | None = None
    phone: str | None = None
    website: str | None = None
    company: Company | None = None


class PostsRouter(
    JSONPlaceholderListMixin,
    CrudRoutes[
        Post,
        ListResult[Post],
        PostQueryParams,
        PostCreate,
        Post,
        PostUpdate,
        Post,
        PostPartialUpdate,
        Post,
    ],
):
    path = "/posts"
    _get_result_model_type = Post
    _get_list_result_model_type = ListResult[Post]
    _create_result_model_type = Post
    _update_result_model_type = Post
    _partial_update_result_model_type = Post

    def get_post_comments(self, post_id: int) -> ListResult[Comment]:
        return self._get_list(f"{self.path}/{post_id}/comments", ListResult[Comment])


class CommentsRouter(
    JSONPlaceholderListMixin,
    CrudRoutes[
        Comment,
        ListResult[Comment],
        CommentQueryParams,
        CommentCreate,
        Comment,
        CommentUpdate,
        Comment,
        CommentPartialUpdate,
        Comment,
    ],
):
    path = "/comments"
    _get_result_model_type = Comment
    _get_list_result_model_type = ListResult[Comment]
    _create_result_model_type = Comment
    _update_result_model_type = Comment
    _partial_update_result_model_type = Comment


class AlbumsRouter(
    JSONPlaceholderListMixin,
    CrudRoutes[
        Album,
        ListResult[Album],
        AlbumQueryParams,
        AlbumCreate,
        Album,
        AlbumUpdate,
        Album,
        AlbumPartialUpdate,
        Album,
    ],
):
    path = "/albums"
    _get_result_model_type = Album
    _get_list_result_model_type = ListResult[Album]
    _create_result_model_type = Album
    _update_result_model_type = Album
    _partial_update_result_model_type = Album

    def get_album_photos(self, album_id: int) -> ListResult[Photo]:
        return self._get_list(f"{self.path}/{album_id}/photos", ListResult[Photo])


class PhotosRouter(
    JSONPlaceholderListMixin,
    CrudRoutes[
        Photo,
        ListResult[Photo],
        PhotoQueryParams,
        PhotoCreate,
        Photo,
        PhotoUpdate,
        Photo,
        PhotoPartialUpdate,
        Photo,
    ],
):
    path = "/photos"
    _get_result_model_type = Photo
    _get_list_result_model_type = ListResult[Photo]
    _create_result_model_type = Photo
    _update_result_model_type = Photo
    _partial_update_result_model_type = Photo


class TodosRouter(
    JSONPlaceholderListMixin,
    CrudRoutes[
        Todo,
        ListResult[Todo],
        TodoQueryParams,
        TodoCreate,
        Todo,
        TodoUpdate,
        Todo,
        TodoPartialUpdate,
        Todo,
    ],
):
    path = "/todos"
    _get_result_model_type = Todo
    _get_list_result_model_type = ListResult[Todo]
    _create_result_model_type = Todo
    _update_result_model_type = Todo
    _partial_update_result_model_type = Todo


class UsersRouter(
    JSONPlaceholderListMixin,
    CrudRoutes[
        User,
        ListResult[User],
        UserQueryParams,
        UserCreate,
        User,
        UserUpdate,
        User,
        UserPartialUpdate,
        User,
    ],
):
    path = "/users"
    _get_result_model_type = User
    _get_list_result_model_type = ListResult[User]
    _create_result_model_type = User
    _update_result_model_type = User
    _partial_update_result_model_type = User

    def get_user_albums(self, user_id: int) -> ListResult[Album]:
        return self._get_list(f"{self.path}/{user_id}/albums", ListResult[Album])

    def get_user_todos(self, user_id: int) -> ListResult[Todo]:
        return self._get_list(f"{self.path}/{user_id}/todos", ListResult[Todo])

    def get_user_posts(self, user_id: int) -> ListResult[Post]:
        return self._get_list(f"{self.path}/{user_id}/posts", ListResult[Post])


class JSONPlaceholderClient(ResticClient):
    def __init__(self) -> None:
        super().__init__(BASE_URL, timeout=10.0)
        self.posts = PostsRouter(self._session, self._async_session, self._logger)
        self.comments = CommentsRouter(self._session, self._async_session, self._logger)
        self.albums = AlbumsRouter(self._session, self._async_session, self._logger)
        self.photos = PhotosRouter(self._session, self._async_session, self._logger)
        self.todos = TodosRouter(self._session, self._async_session, self._logger)
        self.users = UsersRouter(self._session, self._async_session, self._logger)


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


# ruff: disable[F841, T201]
def test_posts_routes(client: JSONPlaceholderClient) -> None:
    posts = client.posts
    post = posts.get(1)
    posts_list = posts.get_list()
    post_created = posts.create(PostCreate(user_id=1, title="title", body="body"))
    post_updated = posts.update(2, PostUpdate(id=2, user_id=1, title="new title", body="new body"))
    post_partially_updated = posts.partial_update(3, PostPartialUpdate(title="new title"))
    posts.delete(4)
    comments_list = posts.get_post_comments(5)


def test_comments_routes(client: JSONPlaceholderClient) -> None:
    comments = client.comments
    comment = comments.get(1)
    comments_list = comments.get_list()
    comment_created = comments.create(
        CommentCreate(post_id=1, name="abcd", email="test@gmail.com", body="body")
    )
    comment_updated = comments.update(
        2,
        CommentUpdate(id=2, post_id=1, name="abcd", email="test@gmail.com", body="body"),
    )
    comment_partially_updated = comments.partial_update(3, CommentPartialUpdate(body="new body"))
    comments.delete(4)


def test_albums_routes(client: JSONPlaceholderClient) -> None:
    albums = client.albums
    album = albums.get(1)
    albums_list = albums.get_list()
    album_created = albums.create(AlbumCreate(user_id=1, title="title"))
    album_updated = albums.update(2, AlbumUpdate(id=2, user_id=1, title="new title"))
    album_partially_updated = albums.partial_update(3, AlbumPartialUpdate(title="new title"))
    albums.delete(4)
    photos_list = albums.get_album_photos(1)


def test_photos_routes(client: JSONPlaceholderClient) -> None:
    photos = client.photos
    photo = photos.get(1)
    photos_list = photos.get_list()
    url = HttpUrl("https://via.placeholder.com/600/92c952")
    photo_created = photos.create(
        PhotoCreate(album_id=1, title="title", url=url, thumbnail_url=url)
    )
    photo_updated = photos.update(
        2, PhotoUpdate(album_id=2, title="new title", url=url, thumbnail_url=url)
    )
    photo_partially_updated = photos.partial_update(3, PhotoPartialUpdate(title="new title"))
    photos.delete(4)


def test_todos_routes(client: JSONPlaceholderClient) -> None:
    todos = client.todos
    todo = todos.get(1)
    todos_list = todos.get_list()
    todo_created = todos.create(TodoCreate(user_id=1, title="title"))
    todo_updated = todos.update(2, TodoUpdate(id=2, user_id=1, title="new title", completed=True))
    todo_partially_updated = todos.partial_update(3, TodoPartialUpdate(completed=True))
    todos.delete(4)


def test_users_routes(client: JSONPlaceholderClient) -> None:
    users = client.users
    user = users.get(1)
    users_list = users.get_list()
    address = Address(
        street="Sesame Street",
        suite="123",
        city="New York",
        zipcode="10128",
        geo=Geolocation(latitude=40.7711, longitude=73.9835),  # pyright: ignore[reportCallIssue]
    )
    company = Company(
        name="Dunder Mifflin", catch_phrase="Limitless paper in a paperless world.", bs=""
    )
    user_created = users.create(
        UserCreate(
            name="Dwight Schrute",
            username="dschrute",
            email="dschrute@dundermifflin.com",
            address=address,
            phone="1-800-984-3672",
            website="schrute-space.com",
            company=company,
        )
    )
    user_updated = users.update(2, UserUpdate(**user_created.model_dump()))
    user_partially_updated = users.partial_update(3, UserPartialUpdate(website="schrute-space.org"))
    users.delete(4)
    albums_list = users.get_user_albums(1)
    todos_list = users.get_user_todos(1)
    posts_list = users.get_user_posts(1)


async def async_example(client: JSONPlaceholderClient) -> None:
    post = await client.posts.async_get(1)
    print(f"Post: {post}")
    posts = await client.posts.async_get_list()
    print(f"Number of posts: {len(posts.results)}")
    new_post = PostCreate(user_id=1, title="Test Post", body="This is a test")
    created_post = await client.posts.async_create(new_post)
    print(f"Created post: {created_post}")
    update_data = PostUpdate(id=post.id, user_id=1, title="Updated Title", body="Updated body")
    updated_post = await client.posts.async_update(post.id, update_data)
    print(f"Updated post: {updated_post}")
    await client.posts.async_delete(created_post.id)
    print("Post deleted")


# ruff: enable[F841, T201]
async def main() -> None:
    # TODO: add error handling examples
    client = JSONPlaceholderClient()
    with client:
        test_posts_routes(client)
        test_comments_routes(client)
        test_albums_routes(client)
        test_photos_routes(client)
        test_todos_routes(client)
        test_users_routes(client)

    async with client:
        await async_example(client)


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
