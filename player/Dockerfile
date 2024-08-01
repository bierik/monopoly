FROM node:22-alpine3.20

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

RUN corepack enable

WORKDIR /app/player

COPY pnpm-lock.yaml package.json ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile

EXPOSE 3000

CMD [ "pnpm", "run", "dev", "--host", "0.0.0.0" ]
