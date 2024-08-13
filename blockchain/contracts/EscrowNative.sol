// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

// Uncomment this line to use console.log
// import "hardhat/console.sol";

contract EscrowNative is Ownable {
    using SafeERC20 for IERC20;
    address public tokenAddress;

    event Deposited(address indexed payer, uint256 amount);
    event Locked(address indexed payer, uint256 amount);
    event Unlocked(address indexed payer, uint256 amount);
    event Paid(address indexed payer, uint256 amount);
    event Refunded(address indexed payer, uint256 amount);
    event Withdrawn(address indexed payer, uint256 amount);

    mapping(address => uint256) private _deposits;
    mapping(address => uint256) private _locked;
    uint256 private _payments;

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

    function payments() public view returns (uint256) {
        return _payments;
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

    function pay(address payer, uint256 amount) public onlyOwner {
        require(_locked[payer] >= amount, "Insufficient funds locked");

        _deposits[payer] -= amount;
        _locked[payer] -= amount;
        _payments += amount;

        emit Paid(payer, amount);
    }

    function refund(uint256 amount) public {
        require(_deposits[msg.sender] - _locked[msg.sender] >= amount, "Insufficient funds to refund");

        _deposits[msg.sender] -= amount;

        payable(msg.sender).transfer(amount);

        emit Refunded(msg.sender, amount);
    }

    function withdraw(uint256 amount) public onlyOwner {
        require(_payments >= amount, "Insufficient funds to withdraw");

        payable(msg.sender).transfer(amount);

        emit Withdrawn(msg.sender, amount);
    }
}
