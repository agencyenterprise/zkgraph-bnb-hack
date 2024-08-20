// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";

// Uncomment this line to use console.log
// import "hardhat/console.sol";

contract EscrowNative is Ownable {
    uint256 public platformFeePercentage = 0;
    address public relayer;

    event Deposited(address indexed payer, uint256 amount);
    event Locked(address indexed payer, uint256 amount);
    event Unlocked(address indexed payer, uint256 amount);
    event Paid(address indexed payer, uint256 amount);
    event Refunded(address indexed payer, uint256 amount);
    event Withdrawn(address indexed payer, uint256 amount);

    mapping(address => uint256) private _deposits;
    mapping(address => uint256) private _locked;
    uint256 private _fees;

    modifier onlyOwnerOrRelayer() {
        require(msg.sender == owner() || msg.sender == relayer, "Caller is not a relayer");
        _;
    }

    constructor(uint256 _platformFeePercentage, address _relayer) Ownable(msg.sender) {
        platformFeePercentage = _platformFeePercentage;
        relayer = _relayer;
    }

    function balanceOf(address _payer) public view returns (uint256) {
        return _deposits[_payer] - _locked[_payer];
    }

    function lockedOf(address _payer) public view returns (uint256) {
        return _locked[_payer];
    }

    function deposit() public payable {
        _deposits[msg.sender] += msg.value;

        emit Deposited(msg.sender, msg.value);
    }

    function fees() public view returns (uint256) {
        return _fees;
    }

    function setPlatformFeePercentage(uint256 _platformFeePercentage) public onlyOwner {
        platformFeePercentage = _platformFeePercentage;
    }

    function lock(address _payer, uint256 _amount) public onlyOwnerOrRelayer {
        require(_deposits[_payer] >= _amount, "Insufficient funds to lock");

        _locked[_payer] += _amount;

        emit Locked(_payer, _amount);
    }

    function unlock(address _payer, uint256 _amount) public onlyOwnerOrRelayer {
        require(_locked[_payer] >= _amount, "Insufficient funds to unlock");

        _locked[_payer] -= _amount;

        emit Unlocked(_payer, _amount);
    }

    function pay(address _payer, address _payee, uint256 _amount) public onlyOwnerOrRelayer {
        require(_locked[_payer] >= _amount, "Insufficient funds locked");

        _deposits[_payer] -= _amount;
        _locked[_payer] -= _amount;
    
        uint256 fee = (_amount * platformFeePercentage) / (100 * 10**18);
        _fees += fee;

        payable(_payee).transfer(_amount - fee);

        emit Paid(_payer, _amount);
    }

    function refund(uint256 _amount) public {
        require(_deposits[msg.sender] - _locked[msg.sender] >= _amount, "Insufficient funds to refund");

        _deposits[msg.sender] -= _amount;

        payable(msg.sender).transfer(_amount);

        emit Refunded(msg.sender, _amount);
    }

    function withdraw(uint256 _amount) public onlyOwner {
        require(_fees >= _amount, "Insufficient funds to withdraw");

        payable(msg.sender).transfer(_amount);

        emit Withdrawn(msg.sender, _amount);
    }
}
