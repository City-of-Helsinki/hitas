FROM public.ecr.aws/docker/library/node:22-alpine AS build

RUN mkdir /hitas
WORKDIR /hitas

ADD package.json ./
ADD yarn.lock ./
RUN yarn install

ADD postcss.config.js ./
ADD public ./public
ADD src ./src
ADD tsconfig.json ./
ADD webpack.config.js ./

RUN yarn build

FROM public.ecr.aws/nginx/nginx-unprivileged:1.23-alpine
COPY --from=build /hitas/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
