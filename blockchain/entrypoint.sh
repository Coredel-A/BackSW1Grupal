#!/bin/sh
set -e

# 1. Arranca el nodo Ethereum local accesible desde otros contenedores
npx hardhat node --hostname 0.0.0.0 &
NODE_PID=$!

# 2. Espera a que el RPC esté listo
echo "Esperando a que el nodo Hardhat acepte conexiones..."
sleep 8

# 3. Despliega el contrato (dirección determinista, ver deploy.js)
npx hardhat run scripts/deploy.js --network localhost || echo "[warn] el deploy falló (¿ya estaba desplegado?)"

# 4. Mantiene el nodo en primer plano
wait "$NODE_PID"
