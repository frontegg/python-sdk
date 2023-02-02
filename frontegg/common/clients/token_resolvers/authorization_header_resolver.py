from typing import Optional
from frontegg.common.clients.token_resolvers.token_resolver import TokenResolver
from frontegg.common.clients.types import TokenTypes, AuthHeaderType, IEntityWithRoles, IValidateTokenOptions


class AuthorizationJWTResolver(TokenResolver[IEntityWithRoles]):
    def __init__(self):
        super().__init__([TokenTypes.TenantApiToken.value, TokenTypes.UserApiToken.value, TokenTypes.UserToken.value], AuthHeaderType.JWT.value)

    def validate_token(
            self,
            token: str,
            public_key: str,
            options: Optional[IValidateTokenOptions] = None
    ) -> IEntityWithRoles:
        entity = super().verify_token(token, public_key)

        if options is not None and (options.get('permissions') or options.get('roles')):
            self.validate_roles_and_permissions(entity, options)

        return entity

    def get_entity(self, entity: IEntityWithRoles) -> IEntityWithRoles:
        return entity
