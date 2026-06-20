// Despliega RegistroRecetas en la red local.
// Al ser el primer despliegue desde la cuenta 0, la dirección es DETERMINISTA:
//   0x5FbDB2315678afecb367f032d93F642f64180aa3
// El backend usa esa dirección (variable CONTRACT_ADDRESS).
const hre = require("hardhat");

async function main() {
  const Factory = await hre.ethers.getContractFactory("RegistroRecetas");
  const contrato = await Factory.deploy();
  await contrato.waitForDeployment();
  const address = await contrato.getAddress();
  console.log("RegistroRecetas desplegado en:", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
