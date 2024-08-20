import hre from "hardhat";
import { expect } from "chai";

describe("Escrow", () => {
  let escrowContract: any;

  let hub: any;
  let client1: any;
  let client2: any;
  let worker1: any;

  beforeEach(async () => {
    [hub, client1, client2, worker1] = await hre.ethers.getSigners();

    const Escrow = await hre.ethers.getContractFactory("EscrowNative");
    escrowContract = await Escrow.deploy(hre.ethers.parseEther("1"), process.env.DEFENDER_RELAYER_ADDRESS!);
  });

  describe("Deployment", () => {
    it("When deploying should set owner address", async () => {
      // Assert
      expect(await escrowContract.owner()).to.equal(hub.address);
      expect(await escrowContract.platformFeePercentage()).to.equal(hre.ethers.parseEther("1"));
      expect(await escrowContract.relayer()).to.equal(process.env.DEFENDER_RELAYER_ADDRESS!);
    });
  });

  describe("Deposit", () => {
    it("Two clients should make deposits", async () => {
      // Arrange
      let client1TokenBalanceA = await hre.ethers.provider.getBalance(
        client1.address
      );
      let client2TokenBalanceA = await hre.ethers.provider.getBalance(
        client2.address
      );
      let escrowTokenBalance = await hre.ethers.provider.getBalance(
        await escrowContract.getAddress()
      );
      let client1EscrowBalance = await escrowContract.balanceOf(
        client1.address
      );
      let client2EscrowBalance = await escrowContract.balanceOf(
        client2.address
      );

      expect(escrowTokenBalance).to.equal(hre.ethers.parseEther("0"));
      expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("0"));
      expect(client2EscrowBalance).to.equal(hre.ethers.parseEther("0"));

      // Act
      await escrowContract.connect(client1).deposit({
        value: hre.ethers.parseEther("3"),
      });
      await escrowContract.connect(client2).deposit({
        value: hre.ethers.parseEther("5"),
      });

      // Assert
      let client1TokenBalanceB = await hre.ethers.provider.getBalance(
        client1.address
      );
      let client2TokenBalanceB = await hre.ethers.provider.getBalance(
        client2.address
      );
      escrowTokenBalance = await hre.ethers.provider.getBalance(
        await escrowContract.getAddress()
      );
      client1EscrowBalance = await escrowContract.balanceOf(client1.address);
      client2EscrowBalance = await escrowContract.balanceOf(client2.address);

      expect(client1TokenBalanceA).to.greaterThan(client1TokenBalanceB);
      expect(client2TokenBalanceA).to.greaterThan(client2TokenBalanceB);
      expect(escrowTokenBalance).to.equal(hre.ethers.parseEther("8"));

      expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("3"));
      expect(client2EscrowBalance).to.equal(hre.ethers.parseEther("5"));
    });
  });

  describe("Payment", () => {
    it("Clients should make payments through escrow", async () => {
      // Arrange
      await escrowContract.connect(client1).deposit({ value: hre.ethers.parseEther("3") });
      await escrowContract.connect(client2).deposit({ value: hre.ethers.parseEther("5") });

      let client1TokenBalanceA = await hre.ethers.provider.getBalance(
        client1.address
      );
      let worker1TokenBalanceA = await hre.ethers.provider.getBalance(
        worker1.address
      );
      let escrowTokenBalance = await hre.ethers.provider.getBalance(
        await escrowContract.getAddress()
      );
      let fees = await escrowContract.fees();
      let client1EscrowBalance = await escrowContract.balanceOf(
        client1.address
      );

      expect(escrowTokenBalance).to.equal(hre.ethers.parseEther("8"));
      expect(fees).to.equal(hre.ethers.parseEther("0"));
      expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("3"));

      // Act -> Client1 pays Worker1
      await escrowContract
        .connect(hub)
        .lock(client1.address, hre.ethers.parseEther("1"));
      await escrowContract
        .connect(hub)
        .pay(client1.address, worker1.address, hre.ethers.parseEther("1"));

      // Assert -> Client1 pays Worker1
      let client1TokenBalanceB = await hre.ethers.provider.getBalance(
        client1.address
      );
      let worker1TokenBalanceB = await hre.ethers.provider.getBalance(
        worker1.address
      );
      escrowTokenBalance = await hre.ethers.provider.getBalance(
        await escrowContract.getAddress()
      );
      fees = await escrowContract.fees();
      client1EscrowBalance = await escrowContract.balanceOf(client1.address);

      expect(client1TokenBalanceA).to.equal(client1TokenBalanceB);
      expect(worker1TokenBalanceB).to.equal(worker1TokenBalanceA + hre.ethers.parseEther("0.99")); // Changed Amount minus platform fee
      expect(escrowTokenBalance).to.equal(hre.ethers.parseEther("7.01")); // Changed -Amount minus platform fee
      expect(fees).to.equal(hre.ethers.parseEther("0.01")); // Changed platform fee
      expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("2")); // Changed -Amount
    });
  });
});
