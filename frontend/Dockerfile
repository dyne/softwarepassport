FROM node:alpine

ENV PORT 3000

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY package*.json /usr/src/app/
RUN npm -g i pnpm
RUN pnpm install

COPY . /usr/src/app

RUN pnpm run build
EXPOSE 3000

CMD "pnpm" "run" "dev"
