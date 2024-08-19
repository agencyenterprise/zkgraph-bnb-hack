// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";

// Uncomment this line to use console.log
// import "hardhat/console.sol";

contract EscrowNative is Ownable {
    uint256 public platformFeePercentage = 0;

    event Deposited(address indexed payer, uint256 amount);
    event Locked(address indexed payer, uint256 amount);
    event Unlocked(address indexed payer, uint256 amount);
    event Paid(address indexed payer, uint256 amount);
    event Refunded(address indexed payer, uint256 amount);
    event Withdrawn(address indexed payer, uint256 amount);

    mapping(address => uint256) private _deposits;
    mapping(address => uint256) private _locked;
    uint256 private _fees;

    constructor() Ownable(msg.sender) {
    }

    function balanceOf(address payer) public view returns (uint256) {
        return _deposits[payer] - _locked[payer];
    }

    function lockedOf(address payer) public view returns (uint256) {
        return _locked[payer];
    }

    function deposit() public payable {
        _deposits[msg.sender] += msg.value;

        emit Deposited(msg.sender, msg.value);
    }

    function fees() public view returns (uint256) {
        return _fees;
    }

    function setPlatformFeePercentage(uint256 feePercentage) public onlyOwner {
        platformFeePercentage = feePercentage;
    }

    function lock(address payer, uint256 amount) public onlyOwner {
        require(_deposits[payer] >= amount, "Insufficient funds to lock");

        _locked[payer] += amount;

        emit Locked(payer, amount);
    }

    function unlock(address payer, uint256 amount) public onlyOwner {
        require(_locked[payer] >= amount, "Insufficient funds to unlock");

        _locked[payer] -= amount;

        emit Unlocked(payer, amount);
    }

    function pay(address payer, address payee, uint256 amount) public onlyOwner {
        require(_locked[payer] >= amount, "Insufficient funds locked");

        _deposits[payer] -= amount;
        _locked[payer] -= amount;
    
        uint256 fee = (amount * platformFeePercentage) / (100 * 10**8);
        _fees += fee;

        payable(payee).transfer(amount - fee);

        emit Paid(payer, amount);
    }

    function refund(uint256 amount) public {
        require(_deposits[msg.sender] - _locked[msg.sender] >= amount, "Insufficient funds to refund");

        _deposits[msg.sender] -= amount;

        payable(msg.sender).transfer(amount);

        emit Refunded(msg.sender, amount);
    }

    function withdraw(uint256 amount) public onlyOwner {
        require(_fees >= amount, "Insufficient funds to withdraw");

        payable(msg.sender).transfer(amount);

        emit Withdrawn(msg.sender, amount);
    }
}
