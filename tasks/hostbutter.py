#!/usr/bin/env python3

from typing import Dict, Optional

import myke


@myke.task_sh
def x_stack_deploy(
    domain: str = myke.arg(env_var="DOMAIN"),
    docker_context: Optional[str] = myke.arg(None, env_var="DOCKER_CONTEXT"),
):
    dot_env_file: str = ".env"
    dot_env: Dict[str, str] = myke.read.dotfile(dot_env_file)

    k: str = "COMPOSE_PROJECT_NAME"
    if k not in dot_env:
        raise Exception(f"Missing {k} in {dot_env_file}")

    if not docker_context:
        docker_context = domain

    return r"""
export IMAGE_REGISTRY="registry.$DOCKER_CONTEXT" \
&& export NOW=$(date +%s) \
&& export "$(grep -m1 '^COMPOSE_PROJECT_NAME=' .env)" \
&& export IMAGE_REPO="${IMAGE_OWNER}/${COMPOSE_PROJECT_NAME}" \
&& if [ "$DOCKER_CONTEXT" != "$DOMAIN" ]; then export COMPOSE_PROJECT_NAME="$(echo ${DOMAIN} | tr . -)_${COMPOSE_PROJECT_NAME}"; fi \
&& (echo 'version: "3.9"' && DOCKER_CONTEXT=default docker compose config) | \
  sed "s/^\([[:space:]]\+name: [a-zA-Z0-9\_\-]\+\_\)\([[:digit:]]\+\)$/\1$NOW/g" | \
  docker stack deploy --prune --with-registry-auth --resolve-image never --compose-file - $COMPOSE_PROJECT_NAME \
&& (docker-stack-wait.sh -s 3 -t 300 -p 10 $COMPOSE_PROJECT_NAME \
|| (docker stack ps $COMPOSE_PROJECT_NAME --no-trunc && exit 1))
"""


if __name__ == "__main__":
    myke.main(__file__)
