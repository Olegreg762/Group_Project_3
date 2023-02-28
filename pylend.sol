
pragma solidity ^0.5.0;

contract LendBorrow {
    address owner = msg.sender;
    mapping(address => uint) public userBalances;


    function lend(uint amount) public {
        require(msg.sender == owner, "Only the owner can lend funds.");
        require(amount > 0, "Invalid loan amount.");

        userBalances[msg.sender] += amount;
    }

    function borrow(uint amount) public {
        require(amount > 0, "Invalid borrow amount.");
        require(userBalances[msg.sender] >= amount, "Insufficient funds.");

        userBalances[msg.sender] -= amount;
    }

    function repay(uint amount) public {
        require(amount > 0, "Invalid repay amount.");
        require(userBalances[msg.sender] <= amount, "Cannot repay more than the borrowed amount.");

        userBalances[msg.sender] += amount;
    }

    function getBalance(address user) public view returns (uint) {
        return userBalances[user];
    }
}