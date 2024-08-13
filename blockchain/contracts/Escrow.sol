// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

// Uncomment this line to use console.log
// import "hardhat/console.sol";

contract Escrow is Ownable {
    using SafeERC20 for IERC20;
    address public tokenAddress;

    event Deposited(address indexed payer, uint256 amount);
    event Locked(address indexed payer, uint256 amount);
    event Unlocked(address indexed payer, uint256 amount);
    event Paid(address indexed payer, address indexed payee, uint256 amount);
    event Withdrawn(address indexed payer, uint256 amount);

    mapping(address => uint256) private _deposits;
    mapping(address => uint256) private _locked;

    constructor(address tokenAddress_) Ownable(msg.sender) {
        require(tokenAddress_ != address(0), "token address cannot be 0");

        tokenAddress = tokenAddress_;
    }

    function balanceOf(address payer) public view returns (uint256) {
        return _deposits[payer] - _locked[payer];
    }

    function lockedOf(address payer) public view returns (uint256) {
        return _locked[payer];
    }

    function deposit(uint256 amount) public {
        _deposits[msg.sender] += amount;

        IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);

        emit Deposited(msg.sender, amount);
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

        IERC20(tokenAddress).approve(address(this), amount);
        IERC20(tokenAddress).safeTransferFrom(address(this), payee, amount);

        emit Paid(payer, payee, amount);
    }

    function withdraw(uint256 amount) public {
        require(_deposits[msg.sender] - _locked[msg.sender] >= amount, "Insufficient funds to withdraw");

        _deposits[msg.sender] -= amount;

        IERC20(tokenAddress).approve(address(this), amount);
        IERC20(tokenAddress).safeTransferFrom(address(this), msg.sender, amount);

        emit Withdrawn(msg.sender, amount);
    }
}
