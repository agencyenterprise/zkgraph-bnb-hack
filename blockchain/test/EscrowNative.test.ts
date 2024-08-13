import hre from "hardhat";
import { expect } from "chai";

describe("Escrow", () => {
  let escrowContract: any;

  let hub: any;
  let client1: any;
  let client2: any;

  beforeEach(async () => {
    [hub, client1, client2] = await hre.ethers.getSigners();

    const Escrow = await hre.ethers.getContractFactory("EscrowNative");
    escrowContract = await Escrow.deploy();
  });

  describe("Deployment", () => {
    it("When deploying should set owner address", async () => {
      // Assert
      expect(await escrowContract.owner()).to.equal(hub.address);
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
      let escrowTokenBalance = await hre.ethers.provider.getBalance(
        await escrowContract.getAddress()
      );
      let payments = await escrowContract.payments();
      let client1EscrowBalance = await escrowContract.balanceOf(
        client1.address
      );

      expect(escrowTokenBalance).to.equal(hre.ethers.parseEther("8"));
      expect(payments).to.equal(hre.ethers.parseEther("0"));
      expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("3"));

      // Act -> Client1 pays Worker1
      await escrowContract
        .connect(hub)
        .lock(client1.address, hre.ethers.parseEther("1"));
      await escrowContract
        .connect(hub)
        .pay(client1.address, hre.ethers.parseEther("1"));

      // Assert 1 -> Client1 pays Worker1
      let client1TokenBalanceB = await hre.ethers.provider.getBalance(
        client1.address
      );
      escrowTokenBalance = await hre.ethers.provider.getBalance(
        await escrowContract.getAddress()
      );
      payments = await escrowContract.payments();
      client1EscrowBalance = await escrowContract.balanceOf(client1.address);

      expect(client1TokenBalanceA).to.equal(client1TokenBalanceB);
      expect(escrowTokenBalance).to.equal(hre.ethers.parseEther("8"));
      expect(payments).to.equal(hre.ethers.parseEther("1")); // Changed +1
      expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("2")); // Changed -1
    });
  });

  // describe("Lock & Unlock", () => {
  //   it("Hub should lock and unlock client funds from escrow", async () => {
  //     // Arrange
  //     await mockedERC20Contract
  //       .connect(client1)
  //       .approve(await escrowContract.getAddress(), hre.ethers.parseEther("3"));
  //     await escrowContract.connect(client1).deposit(hre.ethers.parseEther("3"));
  //     await mockedERC20Contract
  //       .connect(client2)
  //       .approve(await escrowContract.getAddress(), hre.ethers.parseEther("5"));
  //     await escrowContract.connect(client2).deposit(hre.ethers.parseEther("5"));

  //     let escrowTokenBalance = await mockedERC20Contract.balanceOf(
  //       await escrowContract.getAddress()
  //     );
  //     let client1EscrowBalance = await escrowContract.balanceOf(
  //       client1.address
  //     );
  //     let client2EscrowBalance = await escrowContract.balanceOf(
  //       client2.address
  //     );
  //     let client1EscrowLocked = await escrowContract.lockedOf(client1.address);
  //     let client2EscrowLocked = await escrowContract.lockedOf(client2.address);

  //     expect(escrowTokenBalance).to.equal(hre.ethers.parseEther("8"));
  //     expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("3"));
  //     expect(client2EscrowBalance).to.equal(hre.ethers.parseEther("5"));
  //     expect(client1EscrowLocked).to.equal(hre.ethers.parseEther("0"));
  //     expect(client2EscrowLocked).to.equal(hre.ethers.parseEther("0"));

  //     // Act 1 -> Hub locks Client1 funds
  //     await escrowContract
  //       .connect(hub)
  //       .lock(client1.address, hre.ethers.parseEther("2"));

  //     // Assert 1 -> Hub locks Client1 funds
  //     escrowTokenBalance = await mockedERC20Contract.balanceOf(
  //       await escrowContract.getAddress()
  //     );
  //     client1EscrowBalance = await escrowContract.balanceOf(client1.address);
  //     client2EscrowBalance = await escrowContract.balanceOf(client2.address);
  //     client1EscrowLocked = await escrowContract.lockedOf(client1.address);
  //     client2EscrowLocked = await escrowContract.lockedOf(client2.address);

  //     expect(escrowTokenBalance).to.equal(hre.ethers.parseEther("8"));
  //     expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("1")); // Changed -2
  //     expect(client2EscrowBalance).to.equal(hre.ethers.parseEther("5"));
  //     expect(client1EscrowLocked).to.equal(hre.ethers.parseEther("2")); // Changed +2
  //     expect(client2EscrowLocked).to.equal(hre.ethers.parseEther("0"));

  //     // Act 2 -> Hub locks Client2 funds
  //     await escrowContract
  //       .connect(hub)
  //       .lock(client2.address, hre.ethers.parseEther("3"));

  //     // Assert 2 -> Hub locks Client2 funds
  //     escrowTokenBalance = await mockedERC20Contract.balanceOf(
  //       await escrowContract.getAddress()
  //     );
  //     client1EscrowBalance = await escrowContract.balanceOf(client1.address);
  //     client2EscrowBalance = await escrowContract.balanceOf(client2.address);
  //     client1EscrowLocked = await escrowContract.lockedOf(client1.address);
  //     client2EscrowLocked = await escrowContract.lockedOf(client2.address);

  //     expect(escrowTokenBalance).to.equal(hre.ethers.parseEther("8"));
  //     expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("1"));
  //     expect(client2EscrowBalance).to.equal(hre.ethers.parseEther("2")); // Changed -3
  //     expect(client1EscrowLocked).to.equal(hre.ethers.parseEther("2"));
  //     expect(client2EscrowLocked).to.equal(hre.ethers.parseEther("3")); // Changed +3

  //     // Act 3 -> Hub unlocks Client1 funds
  //     await escrowContract
  //       .connect(hub)
  //       .unlock(client1.address, hre.ethers.parseEther("1"));

  //     // Assert 1 -> Hub unlocks Client1 funds
  //     escrowTokenBalance = await mockedERC20Contract.balanceOf(
  //       await escrowContract.getAddress()
  //     );
  //     client1EscrowBalance = await escrowContract.balanceOf(client1.address);
  //     client2EscrowBalance = await escrowContract.balanceOf(client2.address);
  //     client1EscrowLocked = await escrowContract.lockedOf(client1.address);
  //     client2EscrowLocked = await escrowContract.lockedOf(client2.address);

  //     expect(escrowTokenBalance).to.equal(hre.ethers.parseEther("8"));
  //     expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("2")); // Changed +1
  //     expect(client2EscrowBalance).to.equal(hre.ethers.parseEther("2"));
  //     expect(client1EscrowLocked).to.equal(hre.ethers.parseEther("1")); // Changed -1
  //     expect(client2EscrowLocked).to.equal(hre.ethers.parseEther("3"));

  //     // Act 2 -> Hub unlocks Client2 funds
  //     await escrowContract
  //       .connect(hub)
  //       .unlock(client2.address, hre.ethers.parseEther("2"));

  //     // Assert 2 -> Hub unlocks Client2 funds
  //     escrowTokenBalance = await mockedERC20Contract.balanceOf(
  //       await escrowContract.getAddress()
  //     );
  //     client1EscrowBalance = await escrowContract.balanceOf(client1.address);
  //     client2EscrowBalance = await escrowContract.balanceOf(client2.address);
  //     client1EscrowLocked = await escrowContract.lockedOf(client1.address);
  //     client2EscrowLocked = await escrowContract.lockedOf(client2.address);

  //     expect(escrowTokenBalance).to.equal(hre.ethers.parseEther("8"));
  //     expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("2"));
  //     expect(client2EscrowBalance).to.equal(hre.ethers.parseEther("4")); // Changed +2
  //     expect(client1EscrowLocked).to.equal(hre.ethers.parseEther("1"));
  //     expect(client2EscrowLocked).to.equal(hre.ethers.parseEther("1")); // Changed -2
  //   });

  //   it("Hub lock invalid amount on escrow should fail", async () => {
  //     // Arrange
  //     await mockedERC20Contract
  //       .connect(client1)
  //       .approve(await escrowContract.getAddress(), hre.ethers.parseEther("3"));
  //     await escrowContract.connect(client1).deposit(hre.ethers.parseEther("3"));

  //     let client1EscrowBalance = await escrowContract.balanceOf(
  //       client1.address
  //     );
  //     let client1EscrowLocked = await escrowContract.lockedOf(client1.address);

  //     expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("3"));
  //     expect(client1EscrowLocked).to.equal(hre.ethers.parseEther("0"));

  //     // Act & Assert
  //     await expect(
  //       escrowContract
  //         .connect(hub)
  //         .lock(client1.address, hre.ethers.parseEther("4"))
  //     ).to.be.revertedWith("Insufficient funds to lock");
  //   });

  //   it("Hub unlock invalid amount on escrow should fail", async () => {
  //     // Arrange
  //     await mockedERC20Contract
  //       .connect(client1)
  //       .approve(await escrowContract.getAddress(), hre.ethers.parseEther("3"));
  //     await escrowContract.connect(client1).deposit(hre.ethers.parseEther("3"));

  //     let client1EscrowBalance = await escrowContract.balanceOf(
  //       client1.address
  //     );
  //     let client1EscrowLocked = await escrowContract.lockedOf(client1.address);

  //     expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("3"));
  //     expect(client1EscrowLocked).to.equal(hre.ethers.parseEther("0"));

  //     await escrowContract
  //       .connect(hub)
  //       .lock(client1.address, hre.ethers.parseEther("2"));

  //     client1EscrowBalance = await escrowContract.balanceOf(client1.address);
  //     client1EscrowLocked = await escrowContract.lockedOf(client1.address);

  //     expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("1"));
  //     expect(client1EscrowLocked).to.equal(hre.ethers.parseEther("2"));

  //     // Act & Assert
  //     await expect(
  //       escrowContract
  //         .connect(hub)
  //         .unlock(client1.address, hre.ethers.parseEther("3"))
  //     ).to.be.revertedWith("Insufficient funds to unlock");
  //   });
  // });

  // describe("Refund", () => {
  //   it("Clients should get their funds refunded from escrow", async () => {
  //     // Arrange
  //     await escrowContract.connect(client1).deposit(hre.ethers.parseEther("3"));
  //     await escrowContract.connect(client2).deposit(hre.ethers.parseEther("5"));

  //     let client1TokenBalance = await mockedERC20Contract.balanceOf(
  //       client1.address
  //     );
  //     let client2TokenBalance = await mockedERC20Contract.balanceOf(
  //       client2.address
  //     );
  //     let escrowTokenBalance = await mockedERC20Contract.balanceOf(
  //       await escrowContract.getAddress()
  //     );
  //     let client1EscrowBalance = await escrowContract.balanceOf(
  //       client1.address
  //     );
  //     let client2EscrowBalance = await escrowContract.balanceOf(
  //       client2.address
  //     );

  //     expect(client1TokenBalance).to.equal(hre.ethers.parseEther("7"));
  //     expect(client2TokenBalance).to.equal(hre.ethers.parseEther("5"));
  //     expect(escrowTokenBalance).to.equal(hre.ethers.parseEther("8"));
  //     expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("3"));
  //     expect(client2EscrowBalance).to.equal(hre.ethers.parseEther("5"));

  //     // Act 1 -> Client1 withdraws 2
  //     await escrowContract
  //       .connect(client1)
  //       .withdraw(hre.ethers.parseEther("2"));

  //     // Assert 1 -> Client1 withdraws 2
  //     client1TokenBalance = await mockedERC20Contract.balanceOf(
  //       client1.address
  //     );
  //     client2TokenBalance = await mockedERC20Contract.balanceOf(
  //       client2.address
  //     );
  //     escrowTokenBalance = await mockedERC20Contract.balanceOf(
  //       await escrowContract.getAddress()
  //     );
  //     client1EscrowBalance = await escrowContract.balanceOf(client1.address);
  //     client2EscrowBalance = await escrowContract.balanceOf(client2.address);

  //     expect(client1TokenBalance).to.equal(hre.ethers.parseEther("9")); // Changed +2
  //     expect(client2TokenBalance).to.equal(hre.ethers.parseEther("5"));
  //     expect(escrowTokenBalance).to.equal(hre.ethers.parseEther("6")); // Changed -2
  //     expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("1")); // Changed -2
  //     expect(client2EscrowBalance).to.equal(hre.ethers.parseEther("5"));

  //     // Act 2 -> Client2 withdraws 3
  //     await escrowContract
  //       .connect(client2)
  //       .withdraw(hre.ethers.parseEther("3"));

  //     // Assert 2 -> Client2 withdraws 3
  //     client1TokenBalance = await mockedERC20Contract.balanceOf(
  //       client1.address
  //     );
  //     client2TokenBalance = await mockedERC20Contract.balanceOf(
  //       client2.address
  //     );
  //     escrowTokenBalance = await mockedERC20Contract.balanceOf(
  //       await escrowContract.getAddress()
  //     );
  //     client1EscrowBalance = await escrowContract.balanceOf(client1.address);
  //     client2EscrowBalance = await escrowContract.balanceOf(client2.address);

  //     expect(client1TokenBalance).to.equal(hre.ethers.parseEther("9"));
  //     expect(client2TokenBalance).to.equal(hre.ethers.parseEther("8")); // Changed +3
  //     expect(escrowTokenBalance).to.equal(hre.ethers.parseEther("3")); // Changed -3
  //     expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("1"));
  //     expect(client2EscrowBalance).to.equal(hre.ethers.parseEther("2")); // Changed -3
  //   });

  //   it("Client withdraw invalid amount from escrow should fail", async () => {
  //     // Arrange
  //     await mockedERC20Contract
  //       .connect(client1)
  //       .approve(await escrowContract.getAddress(), hre.ethers.parseEther("3"));
  //     await escrowContract.connect(client1).deposit(hre.ethers.parseEther("3"));

  //     let client1EscrowBalance = await escrowContract.balanceOf(
  //       client1.address
  //     );
  //     let client1EscrowLocked = await escrowContract.lockedOf(client1.address);

  //     expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("3"));
  //     expect(client1EscrowLocked).to.equal(hre.ethers.parseEther("0"));

  //     await escrowContract
  //       .connect(hub)
  //       .lock(client1.address, hre.ethers.parseEther("1"));

  //     client1EscrowBalance = await escrowContract.balanceOf(client1.address);
  //     client1EscrowLocked = await escrowContract.lockedOf(client1.address);

  //     expect(client1EscrowBalance).to.equal(hre.ethers.parseEther("2"));
  //     expect(client1EscrowLocked).to.equal(hre.ethers.parseEther("1"));

  //     // Act & Assert
  //     await expect(
  //       escrowContract.connect(client1).withdraw(hre.ethers.parseEther("3"))
  //     ).to.be.revertedWith("Insufficient funds to withdraw");
  //   });
  // });
});
