FROM node:20-slim

WORKDIR /app

# Hardhat necesita estas libs base en algunos entornos
RUN apt-get update && apt-get install -y --no-install-recommends git python3 && rm -rf /var/lib/apt/lists/*

COPY package*.json ./
RUN npm install

COPY . .

# Compila el contrato en build (descarga solc y cachea artefactos)
RUN npx hardhat compile

EXPOSE 8545

RUN chmod +x entrypoint.sh
CMD ["./entrypoint.sh"]
