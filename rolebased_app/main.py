#pragma version 2

# Import from pyteal library all objects
# Import other necessary library from the algosdk package
from pyteal import *
# from algosdk.v2client import algod
# from algosdk import account, mnemonic
# from algosdk.future import transaction
# import base64
# from client_connect import algo_client, params


# Five addresses to be set as ambassadors. For tutorial purpose only
# Let's declare the state storage for the application schema
ronan_bytes = "NHEML642TY3HDM3GS2IVJJJQ4ATD5RUF5SW5LCROFTVWRBMTUJZFCT6MGE"
hiboat_bytes = "TMKWZ63E5DH2JY4GIMZF6SQNXVHT75WM7UR72KGXD3JHFEZMN6ZXVLDDIM"
rodgers_bytes = "OBDPTQDJX56N5L7W7LUDF5TSYKSFOWTIXMLESLGVHAJY74PJRPVEHV4GPE"
godrace_bytes = "BLULTMZXFUDPF3MNHYPVR5UPPAEIOXBBUYC4IDDSNKG5SZ52YHMCTDE7A4"
hasanacikgoz_bytes = "KCKKQ6TGKQUZXAN2GF2GVEF3BXVQMNL2U7WUH756OMPAGUIBXLIA4AUUFE"

# Setting the global properties.
# Explicitly define the owner of the contract.
# Declare the five ambassador of types Bytes. We will fill them with a 32 Bytes address
# address type i.e an Algorand address.
# Declare the date, amount of reward and total amount of asset in the contract balance.
# Set the total supply as the balance of asset this account is holding at this time.
# And reserve to zero initially.
def approval_program():
    # Get asset balance of the originator using ID 10403144
    asset_balance = Int(700000) # or use this method: AssetHolding.balance(Int(0), Int(10403144))

    on_creation = Seq([
        App.globalPut(Bytes("owner"), Txn.sender()),
        Assert(Txn.application_args.length() == Int(5)),
        App.globalPut(Bytes("rodgers"), Addr(rodgers_bytes)),
        App.globalPut(Bytes("godrace"), Addr(godrace_bytes)),
        App.globalPut(Bytes("hiboat"), Addr(hiboat_bytes)),
        App.globalPut(Bytes("hasanacikgoz"), Addr(hasanacikgoz_bytes)),
        App.globalPut(Bytes("ronan"), Addr(ronan_bytes)),
        App.globalPut(Bytes("approved_pay_date"), Add(Global.latest_timestamp(), Int(2419200))),
        App.globalPut(Bytes("set_reward_per_head"), Int(5000)),
        App.globalPut(Bytes("total_supply"), asset_balance),
        App.globalPut(Bytes("reserve"), Int(0)),
        Return(Int(1))
    ])

# Get the owner.
# The amount of argument to parse in this case must not exceed 1
# Parse the amount of reward.
# On_closeout:
         # Total supply is the amount of asset balance of the contract owner.
         # This will be deposited to the contract.
         # Set this address as the authorized account.
         # Total authorized amount in the reward pool will be the amount specified
         # in the argument list.
    is_owner = Txn.sender() == App.globalGet(Bytes("owner"))
    reward_pool_amount = Int(500000)
    on_closeout = Seq([
        App.localPut(Int(0), Bytes("authorization_account"), Int(1)),
        App.globalPut(Bytes("approved_bonus_pool"), reward_pool_amount),
        App.globalPut(Bytes("reserve"), Minus(App.globalGet(Bytes("total_supply")), reward_pool_amount)),
        Return(Int(1))
    ])

    # Performing few checks on account interacting with the smart contract i.e ambassadors
    # before allowing to proceeding
    # Check if sender is authorized and or exist
    # Set approval for them.
    # Increase the count

    # Check if caller is registered globally and,
    # Check for a signature - counter that it exist. If true,
    # register a few identification keys such as balance, opted_count, is_ambassador and
    # pay_Count.
    # then identify caller with: write balance,call frequency, ambassador tag
    # and if already got paid within 28 days, else, the transaction is invalid.
    asq = Seq([
        App.localPut(Int(0), Bytes("balance"), Int(0)),
        App.localPut(Int(0), Bytes("Opted_count"), Int(1)),
        App.localPut(Int(0), Bytes("is_ambassador"), Int(1)),
        App.localPut(Int(0), Bytes("pay_count"), Int(0)),
        Return(Int(1))
    ])

    reg_address = If(
        Eq(
            Btoi(Txn.sender()),
            Or(
                App.globalGet(Bytes("godrace")),
                App.globalGet(Bytes("hiboat")),
                App.globalGet(Bytes("hasanacikgoz")),
                App.globalGet(Bytes("rodgers")),
                App.globalGet(Bytes("ronan"))
            )
        ),
        asq,
        Return(Int(0))
    )

    # Transfer function to credit pre-selected accounts. This will be called later in the
    # program.
    # Pay attention to every of code and what they do

    # Pointing to the first argument in the application argument array list.
    # Use for passing argument
    amount = Btoi(Txn.application_args[0])

    # Expressions that must evaluate to an integer of TealType 64 bit unsigned integer.
    # Firstly,reduce the balance in the reward pool by the amount parsed, add it to the
    # balance of the caller (in this case the creator), then write it to storage of account[0]
    # in the list of Txn.accounts(). In this case, the Int(0)index to the current account interacting with the contract.
    # Increment the counter already written to the local storage i.e caller's storage
    xsfer_asset = Seq([
        Assert(App.localGet(Int(0), Bytes("is_ambassador")) == Int(1)),
        App.globalPut(Bytes("approved_bonus_pool"), Minus(App.globalGet(Bytes("approved_bonus_pool")), amount)),
        App.localPut(Int(0), Bytes("balance"), Add(App.localGet(Int(0), Bytes("balance")), amount)),
        App.localPut(Int(0), Bytes("pay_count"), Add(App.localGet(Int(0), Bytes("pay_count")), Int(1))),
        App.localPut(Int(0), Bytes("pay_time"), Global.latest_timestamp())
    ])

    # Utility for claiming reward.
    # Check that the claiming period is within approved date.
    # If the opted account does have the pay_count property i.e has been paid before now, has
    # opted in or has opted, if has the pay_count property, ensure that the next pay date
    # is 28 days in future from the last payment hence the Int(2419200)
    # If any of this condition is met, execute the payment.
    claim_reward = Seq([
        Assert(Txn.type_enum() == Int(6)),  # This must be an application call.
        Assert(Ge(Global.latest_timestamp(), App.globalGet(Bytes("approved_pay_date")))),
        Eq(App.localGet(Int(0), Bytes("pay_count")), Int(0)),
        reg_address,
        Ge(App.localGet(Int(0), Bytes("pay_count")), Int(0)),
        Ge(Global.latest_timestamp(), Add(App.globalGet(Bytes("approved_pay_date")), Int(2419200))),
        Assert(Gt(Global.latest_timestamp(), App.localGet(Int(0), Bytes("pay_time")))),
        Return(Int(1))
    ])

    # Here the heart of tne SM-C which is a chain of test conditions whose value must evaluate to Int(1)else, fails.
    # Set of conditions determining how the contract logic should run.
    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(is_owner)],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_owner)],
        [Txn.on_completion() == OnComplete.CloseOut, on_closeout],
        [Txn.on_completion() == OnComplete.OptIn, reg_address],
        # If the claim reward feed is invoked, then forward asset transfer. Note that the conditions inside the
        # claim_reward field is executed first before proceeding to transfer asset.
        [Txn.type_enum().field == claim_reward, xsfer_asset]
    )
    return program


with open('role_based_approval.teal', 'w') as y:
    compiled = compileTeal(approval_program(), Mode.Application)
    y.write(compiled)
