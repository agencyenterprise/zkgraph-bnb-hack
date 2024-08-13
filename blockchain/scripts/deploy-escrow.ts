import hre from "hardhat";

async function main() {
  console.log("Deploying...");
  const Escrow = await hre.ethers.getContractFactory("Escrow");
  const escrow = await Escrow.deploy(process.env.TOKEN_ADDRESS!);

  console.log("Contract deployed at:", await escrow.getAddress());
}

main().catch((error) => {
  console.log(error);
  process.exitCode = 1;
});
