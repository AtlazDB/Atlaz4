# Back-end (Spring Boot, Java 17). O codigo vem de src/backend, baixado pelo deploy.sh.
# As imagens eclipse-temurin tem versao ARM, entao o build roda direto na VM Ampere.

FROM eclipse-temurin:17-jdk AS build
WORKDIR /build
COPY src/backend/ .
# mvnw esta sem permissao de execucao no git, por isso "sh mvnw".
# O cache do ~/.m2 evita baixar todas as dependencias a cada deploy.
RUN --mount=type=cache,target=/root/.m2 sh mvnw -B -q -DskipTests package

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /build/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
