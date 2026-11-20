FROM likec4/likec4:latest

WORKDIR /app

COPY diagrams ./diagrams/

RUN likec4 build -o /app/dist

FROM nginx:alpine

COPY --from=0 /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
