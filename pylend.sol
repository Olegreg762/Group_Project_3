pragma solidity 0.5.0;

//Create LendBorrow contract
contract LendBorrow {
    mapping(address => uint256) public borrowBalance;
    uint256 public lendBalance;
    uint256 public contractBalance;

    //Constructor to allow the contract to be deployed with an ETH balance
    constructor() public payable{
        contractStart();
    }

    //Event functions allows action to be emitted
    event Lend(address indexed depositor, uint256 amount);
    event Borrow(address indexed borrower, uint256 amount);
    event Repay(address indexed borrower, uint256 amount);
    event Withdraw(address indexed withdraw, uint256 amount);

    //Function to deploy contract with ETH balance
    function contractStart() public payable {
        require(msg.value > 0, "Amount must be greater than zero");

        contractBalance += msg.value;
    }

    //Lend function allows the user to lend ETH to function
    function lend() public payable{
        require(msg.value > 0, "Amount must be greater than zero");

        contractBalance += msg.value;
        lendBalance += msg.value;
        //Broadcast the Lend
        emit Lend(msg.sender, msg.value);
    }
    //Borrow function so user can borrow against the amount lend
    function borrow(uint256 amount) public {
        require(amount > 0, "Amount must be greater than zero");
        require(lendBalance >= amount, "Borrow Amount must be less than Amount Lended");

        borrowBalance[msg.sender] += amount;
        contractBalance -= amount;
        //Broadcast the Borrow
        emit Borrow(msg.sender, amount);
    }
    //Function to repay borrowed amount
    function repay(uint256 amount) public payable {
        amount = msg.value;
        require(amount > 0, "Amount must be greater than zero");
        require(msg.value <= amount, "Repay must be less than amount borrrowed");
        require(borrowBalance[msg.sender] >= amount, "No Borrow Amount to Repay");

        borrowBalance[msg.sender] -= amount;
        contractBalance += amount;
        //Broadcast the Repay amount
        emit Repay(msg.sender, amount);
    }

    function withdraw (uint256 amount) public{
        require(amount > 0, "Amount must be greater than zero");
        require(lendBalance >= amount, "No Funds to Withdraw");

        lendBalance -= amount;
        contractBalance -= amount;

        emit Withdraw(msg.sender, amount);
    }

}
