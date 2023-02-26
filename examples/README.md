# pydantic_sqs/examples

These examples show off using pydantic-sqs.

They require either a valid AWS SQS Queue or an equivalent that can be used with aiobotocore. An example equivalent is Localstack <https://hub.docker.com/r/localstack/localstack>

To run the examples, export your needed AWS variables, your queue name, and any extra variables, then run the example.

Example with AWS_PROFILE

```shell
AWS_PROFILE=myprofile SQS_QUEUE_URL=https://sqs.us-east-2.amazonaws.com/123456789012/MyQueue python basic/example.py
[ThisModel(message_id='efc7d77a-1b46-ca06-4a06-72ef5f2d92f0', receipt_handle='zjdshqidyixeufeznjsrkqzhrherqfnocbmtokfnirjmrbejysdvrdcuekwmagnnphqhfforunppogfhdqhfbgsfzrsanihqrpwgmjspjghmigayjczkafyfjiakdubvcbowcupywuldtusjibtccfydjhmgkdyfkyixlpfziejaqkyomugtsvath', attributes=None, deleted=False, foo='1234'),
 ThatModel(message_id='54b9ed0d-43f6-bd18-e64c-fa3a2a186b27', receipt_handle='fpzuudfsjueseqvikligcevarnxzdczmztadmrskrjzjdkftotaqiaxsldcqjzywsmeqmsqacpxeqxcvcdmykqhoucmyzqtmbvoyoknqnktfahrqzfhelvxmiemcqppsgeroyslzueuefnztimryfkrujgqxgnievtmrvebojtfxqtpbzpzaxherz', attributes=None, deleted=False, bar='5678')]
deleted all the messages we got from the queue
[ThisModel(message_id='efc7d77a-1b46-ca06-4a06-72ef5f2d92f0', receipt_handle='zjdshqidyixeufeznjsrkqzhrherqfnocbmtokfnirjmrbejysdvrdcuekwmagnnphqhfforunppogfhdqhfbgsfzrsanihqrpwgmjspjghmigayjczkafyfjiakdubvcbowcupywuldtusjibtccfydjhmgkdyfkyixlpfziejaqkyomugtsvath', attributes=None, deleted=True, foo='1234'),
 ThatModel(message_id='54b9ed0d-43f6-bd18-e64c-fa3a2a186b27', receipt_handle='fpzuudfsjueseqvikligcevarnxzdczmztadmrskrjzjdkftotaqiaxsldcqjzywsmeqmsqacpxeqxcvcdmykqhoucmyzqtmbvoyoknqnktfahrqzfhelvxmiemcqppsgeroyslzueuefnztimryfkrujgqxgnievtmrvebojtfxqtpbzpzaxherz', attributes=None, deleted=True, bar='5678')]
```

Example using localstack. See the repo's Makefile for an example of how to run localstack in docker

```shell
AWS_ACCESS_KEY_ID=x AWS_SECRET_ACCESS_KEY=x AWS_DEFAULT_REGION=us-east-1 SQS_QUEUE_URL=http://localhost:4566/000000000000/test SQS_ENDPOINT_URL="http://localhost:4566" SQS_USE_SSL=false python basic/example.py
[ThisModel(message_id='0433f635-f21e-ebea-a852-c4b74a18640d', receipt_handle='xoqmqewhdatcxeojccicdqmvfjmybnzfqykphfjrcmjesnrbliiosfjqecgcryqyxwqjkonwvixabwwopkbphcldtebagvoykllcuosaogkcrpocckjhpwmstztoiudwlsdokepnbyyvrytdvvxlrtscyhrthqafycmdvmeumzuqnbdxstaawuhxx', attributes=None, deleted=False, foo='1234'),
ThatModel(message_id='0cb51061-511a-9a71-8fbf-5c3b03bb160c', receipt_handle='gohhxweiadpsafprlxrffzxedsepjqsvfwpsbfkeddvglseognnlgxnbiffzlhbbwccpvqsroqlzquwvresnjgbzazjrirmkqyujvnracenwhbzsvagimznicqsxqdmvxrimzqxuxhanjyyqicvtfpinwewsbpuwkborbezubliuqpdjkoupyajys', attributes=None, deleted=False, bar='5678')]
deleted all the messages we got from the queue
[ThisModel(message_id='0433f635-f21e-ebea-a852-c4b74a18640d', receipt_handle='xoqmqewhdatcxeojccicdqmvfjmybnzfqykphfjrcmjesnrbliiosfjqecgcryqyxwqjkonwvixabwwopkbphcldtebagvoykllcuosaogkcrpocckjhpwmstztoiudwlsdokepnbyyvrytdvvxlrtscyhrthqafycmdvmeumzuqnbdxstaawuhxx', attributes=None, deleted=True, foo='1234'),
ThatModel(message_id='0cb51061-511a-9a71-8fbf-5c3b03bb160c', receipt_handle='gohhxweiadpsafprlxrffzxedsepjqsvfwpsbfkeddvglseognnlgxnbiffzlhbbwccpvqsroqlzquwvresnjgbzazjrirmkqyujvnracenwhbzsvagimznicqsxqdmvxrimzqxuxhanjyyqicvtfpinwewsbpuwkborbezubliuqpdjkoupyajys', attributes=None, deleted=True, bar='5678')]
```
