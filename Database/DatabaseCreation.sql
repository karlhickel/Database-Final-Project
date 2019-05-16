CREATE TABLE users (
  userName VARCHAR(20) PRIMARY KEY,
  fullName VARCHAR(20),
  password VARCHAR(20),
  creditCard VARCHAR(50)
);

CREATE TABLE businessInfo (
  businessName VARCHAR(50) PRIMARY KEY NOT NULL,
  address VARCHAR(50),
  state varchar(20)
);


create table transactions
(
	ID int auto_increment,
	userName varchar(20) not null,
	amount real not null,
	DOT date not null,
	businessName varchar(50),
	constraint transactions_1_pk
		primary key (ID),
	constraint transactions_1__businessName_fk
		foreign key (businessName) references businessInfo (businessName),
	constraint transactions_1__userName_fk
		foreign key (userName) references users (userName)
);

create table balance
(
	userName VARCHAR(20) not null,
	balance REAL,
	ID int auto_increment,
	constraint balance_1_pk
		primary key (ID),
	constraint balance_1__userName_fk
		foreign key (userName) references users (userName)
);



create procedure stateTransactionCount(IN userName VARCHAR(20))
BEGIN
SELECT businessInfo.state,count(businessInfo.state) Count
FROM businessInfo,transactions
WHERE transactions.businessName = businessInfo.businessName
AND transactions.userName = userName
GROUP BY state;
END;



create procedure averageIncomeExpense(IN userNameInput VARCHAR(20))
BEGIN
SELECT DISTINCT (SELECT AVG(amount) FROM transactions WHERE amount > 0 AND userName = userNameInput ) pos,
  (SELECT AVG(amount) FROM transactions WHERE amount < 0 AND username = userNameInput) neg FROM transactions;
END;


create procedure updateUsername(IN oldUserName VARCHAR(20), newUserName Varchar(20))
BEGIN
  START TRANSACTION;
  Update users SET users.userName = newUserName
  WHERE users.userName = oldUserName;

  UPDATE transactions set transactions.userName = newUserName
  WHERE transactions.userName = oldUserName;

  UPDATE balance SET balance.userName = newUserName
  WHERE balance.userName = oldUserName;
  COMMIT;
END;


create procedure deleteUsername(IN oldUserName VARCHAR(20))
BEGIN
  START TRANSACTION;

  DELETE FROM transactions
  WHERE transactions.userName = oldUserName;

  DELETE FROM balance
  WHERE balance.userName = oldUserName;

  DELETE FROM users
  WHERE users.userName = oldUserName;


  COMMIT;
END;

CREATE INDEX userNameID
ON transactions(userName,ID);



create procedure updateCreditCard(in inputUserName varchar(20), IN newCreditCard varchar(50))
BEGIN
  START TRANSACTION;
  Update users SET users.creditCard = newCreditCard
  WHERE users.userName = inputUserName;
  COMMIT;
end;

create procedure updateFullName(IN inputUserName varchar(20), IN newFullName varchar(20))
BEGIN
  START TRANSACTION;
  UPDATE users set users.fullName = newFullName
  WHERE users.userName = inputUserName;
  COMMIT;
end;


update users set users.password = 'maleman'
WHERE users.userName = 'jarlPickel';

SELECT userName, (SELECT  MAX(amount) FROM transactions) - (SELECT MIN(amount) FROM transactions)
FROM transactions
GROUP BY userName;


create procedure viewAccount(userNameInput VARCHAR(50))
BEGIN
  start transaction;
    SELECT users.fullName, balance.balance, users.creditCard, MAX(transactions.DOT)
    FROM users, balance, transactions
    WHERE users.userName = balance.userName AND users.userName = transactions.userName
    AND users.userName = userNameInput
    GROUP BY users.fullName, balance.balance, users.creditCard;
  commit;
end;



create view yearFilter
AS
SELECT DISTINCT YEAR(DOT) as year
FROM transactions;



create procedure yearFilterUpdate()
begin
  start transaction;
  drop view yearFilter;
  create view yearFilter
  AS
  SELECT DISTINCT YEAR(DOT) as year
  FROM transactions;
  commit;
end;


create procedure updateTransactions(amountInput REAL, buisnessNameInput varchar(50), userNameInput varchar(50))
BEGIN
  start transaction;
    INSERT INTO transactions(userName, amount, DOT, businessName)
    VALUES (userNameInput,amountInput,current_date,buisnessNameInput);

    update balance SET balance = ((select b.balance from (SELECT * FROM balance) b where userName =  userNameInput) + amountInput)
    WHERE userName = userNameInput;
  commit;
end;




create procedure updateInsertBusiness(businessNameInput varchar(50), addressInput varchar(50), stateInput varchar(20))
BEGIN
  start transaction;
  insert into businessInfo(businessName, address, state)
  VALUES (businessNameInput, addressInput, stateInput);
  commit;
end;
