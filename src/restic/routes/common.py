from typing import Generic

from restic.routes._models import (
    TCreate,
    TCreateResult,
    TListResultModel,
    TPartialUpdate,
    TPartialUpdateResult,
    TQueryParams,
    TResultModel,
    TUpdate,
    TUpdateResult,
)
from restic.routes.mixins import (
    DeleteMixin,
    GetMixin,
    ListMixin,
    PatchMixin,
    PostMixin,
    PutMixin,
)

ResourceId = int | str


class _BaseRoute:
    path: str


class GetRoute(GetMixin, _BaseRoute, Generic[TResultModel]):
    _get_result_model_type: type[TResultModel]

    def get(self, resource_id: ResourceId) -> TResultModel:
        return self._get(f"{self.path}/{resource_id}", self._get_result_model_type)

    async def async_get(self, resource_id: ResourceId) -> TResultModel:
        return await self._async_get(f"{self.path}/{resource_id}", self._get_result_model_type)


class ListRoute(
    ListMixin,
    _BaseRoute,
    Generic[TListResultModel, TQueryParams],
):
    _get_list_result_model_type: type[TListResultModel]

    def get_list(self, params: TQueryParams | None = None) -> TListResultModel:
        return self._get_list(self.path, self._get_list_result_model_type, params)

    async def async_get_list(self, params: TQueryParams | None = None) -> TListResultModel:
        return await self._async_get_list(self.path, self._get_list_result_model_type, params)


class CreateRoute(PostMixin, _BaseRoute, Generic[TCreate, TCreateResult]):
    _create_result_model_type: type[TCreateResult]

    def create(self, model: TCreate) -> TCreateResult:
        return self._post(self.path, model=model, result_model_type=self._create_result_model_type)

    async def async_create(self, model: TCreate) -> TCreateResult:
        return await self._async_post(
            self.path,
            model=model,
            result_model_type=self._create_result_model_type,
        )


class UpdateRoute(PutMixin, _BaseRoute, Generic[TUpdate, TUpdateResult]):
    _update_result_model_type: type[TUpdateResult]

    def update(
        self,
        resource_id: ResourceId,
        model: TUpdate,
    ) -> TUpdateResult:
        return self._put(
            f"{self.path}/{resource_id}",
            model=model,
            result_model_type=self._update_result_model_type,
        )

    async def async_update(
        self,
        resource_id: ResourceId,
        model: TUpdate,
    ) -> TUpdateResult:
        return await self._async_put(
            f"{self.path}/{resource_id}",
            model=model,
            result_model_type=self._update_result_model_type,
        )


class PartialUpdateRoute(
    PatchMixin,
    _BaseRoute,
    Generic[TPartialUpdate, TPartialUpdateResult],
):
    _partial_update_result_model_type: type[TPartialUpdateResult]

    def partial_update(
        self,
        resource_id: ResourceId,
        model: TPartialUpdate,
    ) -> TPartialUpdateResult:
        return self._patch(
            f"{self.path}/{resource_id}",
            model=model,
            result_model_type=self._partial_update_result_model_type,
        )

    async def async_partial_update(
        self,
        resource_id: ResourceId,
        model: TPartialUpdate,
    ) -> TPartialUpdateResult:
        return await self._async_patch(
            f"{self.path}/{resource_id}",
            model=model,
            result_model_type=self._partial_update_result_model_type,
        )


class DeleteRoute(DeleteMixin, _BaseRoute):
    def delete(self, resource_id: ResourceId) -> None:
        return self._delete(f"{self.path}/{resource_id}")

    async def async_delete(self, resource_id: ResourceId) -> None:
        return await self._async_delete(f"{self.path}/{resource_id}")


class CrudRoutes(
    GetRoute[TResultModel],
    ListRoute[TListResultModel, TQueryParams],
    CreateRoute[TCreate, TCreateResult],
    UpdateRoute[TUpdate, TUpdateResult],
    PartialUpdateRoute[TPartialUpdate, TPartialUpdateResult],
    DeleteRoute,
    Generic[
        TResultModel,
        TListResultModel,
        TQueryParams,
        TCreate,
        TCreateResult,
        TUpdate,
        TUpdateResult,
        TPartialUpdate,
        TPartialUpdateResult,
    ],
):
    pass
