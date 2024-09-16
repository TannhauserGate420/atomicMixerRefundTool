# AtomicMixer RefundTool

## Installation

```
python3 -m venv venv
. venv/bin/activate
pip install atomicmixer
atomicmixer
```

## Walkthrough

1. **If something went wrong (amount to low in this case) simply refund your sats!**

   ![refund1](https://github.com/TannhauserGate420/atomicMixerRefundTool/blob/main/atomicmixer/images/refund_1.jpg)

2. **Install and start the tool:**

   ![refund2](https://github.com/TannhauserGate420/atomicMixerRefundTool/blob/main/atomicmixer/images/refund_2.jpg)

3. **Load your refund file:**

   ![refund3](https://github.com/TannhauserGate420/atomicMixerRefundTool/blob/main/atomicmixer/images/refund_3.jpg)

4. **Enter your private key ([WIF](https://en.bitcoin.it/wiki/Wallet_import_format)):**

   ![refund4](https://github.com/TannhauserGate420/atomicMixerRefundTool/blob/main/atomicmixer/images/refund_4.jpg)

5. **You will get an error if the refund blockheight is not reached yet (144 blocks/~24 hours):**

   ![refund5](https://github.com/TannhauserGate420/atomicMixerRefundTool/blob/main/atomicmixer/images/refund_5.jpg)

6. **After the 144 blocks you are able to refund your coins:**

   ![refund6](https://github.com/TannhauserGate420/atomicMixerRefundTool/blob/main/atomicmixer/images/refund_6.jpg)

## Refund transaction:

   [mempool.space](https://mempool.space/tx/68ccff69c32ff0a5d1fc2b1b7374d036dd1b6c0ecbdc2dcf90d1f71ac7425e61)

## Dependency:

   **This tool depends at the [Mempool API](https://mempool.space/docs/api/rest) to fetch the actual network fees/blockheight and to broadcast the transaction.**

## Donations

**I do not accept donations. If you have some sats left donate them to the [Torproject](https://donate.torproject.org/cryptocurrency/) or to the [EFF](https://supporters.eff.org/donate/join-eff-4).**
