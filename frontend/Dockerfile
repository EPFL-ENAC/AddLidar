FROM node:20-alpine as potree-build-stage
WORKDIR /app
COPY package*.json ./
COPY npm-shrinkwrap.json ./
COPY src ./src
COPY libs ./libs
COPY resources ./resources
COPY *.js ./
COPY *.sh ./
RUN npm ci
# COPY .env ./
RUN npm run build-potree


FROM node:20-alpine as vue-build-stage
WORKDIR /app
COPY vueSrc ./vueSrc
COPY package*.json ./
COPY --from=potree-build-stage /app/libs /app/vueSrc/public/libs
COPY --from=potree-build-stage /app/build /app/vueSrc/public/build
COPY npm-shrinkwrap.json ./
COPY *.js ./
COPY *.ts ./
COPY *.json ./
RUN npm ci
# COPY .env ./
RUN npm run build



FROM nginx:stable-alpine as production-stage

RUN apk add --update bash && rm -rf /var/cache/apk/*

RUN mkdir /app
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=vue-build-stage /app/vueSrc/dist ./app
EXPOSE 80

# COPY entrypoint.sh /app/entrypoint.sh
# ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["nginx", "-g", "daemon off;"]
