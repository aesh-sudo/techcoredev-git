dockerfile:
```
FROM node:18-alpine AS builder
WORKDIR /app

RUN npx create-react-app my-app .
RUN echo 'function App() { return <h1 style={{textAlign:"center",marginTop:"50px"}}>Hello, World!</h1>; } export default App;' > src/App.js
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
```
```npx``` – инструмент «Node.js», который позволяет временно скачать и запустить пакет для создания React-проекта, не устанавливая его глобально.<br>
Далее мы подготавливаем компонент, который при сборке будет вставлен в файл ```public/index.html``` и собираем проект.<br>
```public``` – стандартная директория, которую генерирует ```create-react-app``` при создании проекта.
Во втором слое мы помещаем файлы проекта в определенный каталог веб-сервера «nginx».
