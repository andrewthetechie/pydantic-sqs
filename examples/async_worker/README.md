# async_worker Example

This is a basic sender/worker example using pydantic-sqs.

## Running the Example

### Pre-requisites

You must have a SQS Queue URL and working AWS creds that can acces that queue.

The makefile has some steps you can use to create a queue using localstack. Run `make` to see the help text on how to set this up

### Running

These examples assume you're using the localstack setup. If not, just change the environment variables to match your AWS account and remove the endpoint and SSL variables

#### Sender

Run

```shell
 AWS_ACCESS_KEY_ID=x AWS_SECRET_ACCESS_KEY=x AWS_DEFAULT_REGION=us-east-1  SQS_QUEUE_URL=http://localhost:4566/000000000000/test SQS_ENDPOINT_URL=http://localhost:4566 SQS_USE_SSL=False python sender.py
message_id=None receipt_handle=None attributes=None deleted=False uuid='d9f1fb13-3738-4779-bfa0-63cf321d71f5' message='This is message 0'
Sleeping 5.0 seconds
message_id=None receipt_handle=None attributes=None deleted=False uuid='a4749fe5-5cee-4e56-8b01-57d640220459' message='This is message 1'
Sleeping 5.0 seconds
message_id=None receipt_handle=None attributes=None deleted=False uuid='ff23c113-ac04-4534-a54b-cc9cc43122a8' message='This is message 2'
Sleeping 5.0 seconds
message_id=None receipt_handle=None attributes=None deleted=False uuid='eeca0cbe-7bba-41db-b63c-9fe91350739d' message='This is message 3'
Sleeping 5.0 seconds
message_id=None receipt_handle=None attributes=None deleted=False uuid='96759e7d-a2a5-41b3-8a66-7545fc521efd' message='This is message 4'
Sleeping 5.0 seconds
message_id=None receipt_handle=None attributes=None deleted=False uuid='7cbb41f4-2a54-4cf5-80ac-0d964b8ee766' message='This is message 5'
Sleeping 5.0 seconds
message_id=None receipt_handle=None attributes=None deleted=False uuid='16a6af41-7224-415a-9052-6ddf8b58870b' message='This is message 6'
Sleeping 5.0 seconds
message_id=None receipt_handle=None attributes=None deleted=False uuid='4f77dd16-a9ce-4d1a-aa24-607de6e0218e' message='This is message 7'
Sleeping 5.0 seconds
message_id=None receipt_handle=None attributes=None deleted=False uuid='6ac9df84-1c81-4ba5-9cd2-a313dc12ce5f' message='This is message 8'
Sleeping 5.0 seconds
message_id=None receipt_handle=None attributes=None deleted=False uuid='f7ae1210-cb0b-450f-bf64-cc64b8de7eb6' message='This is message 9'
Sleeping 5.0 seconds
message_id=None receipt_handle=None attributes=None deleted=False uuid='89c8187d-bf8e-4ee1-be90-faccb474a08c' message='This is message 10'
Sleeping 5.0 seconds
message_id=None receipt_handle=None attributes=None deleted=False uuid='2b279610-2a81-4eb1-8984-247814009a26' message='This is message 11'
```

You can kill the sender with Ctrl-C

#### Worker

Run this in another shell

```shell
AWS_ACCESS_KEY_ID=x AWS_SECRET_ACCESS_KEY=x AWS_DEFAULT_REGION=us-east-1  SQS_QUEUE_URL=http://localhost:4566/000000000000/test SQS_ENDPOINT_URL=http://localhost:4566 SQS_USE_SSL=False python worker.py
Deleting task: message_id='b08471c2-ad57-3013-21b3-b799ac887fd1' receipt_handle='wwfmjvkuzdtzwvwrivdnzieluvcnwakbaflaikhlaopvftgzopayfaausswfcbuwgslxdrdqylbjcrhdogfqxqkidegwiqfibvulnnfwczoexhteloelvbinalwcwogyntvkncyctzptkedwtcehnjftujmwsytjaduetiylzgzgeskzsaovsswrj' attributes=None deleted=False uuid='d9f1fb13-3738-4779-bfa0-63cf321d71f5' message='This is message 0'
Deleting task: message_id='3e328543-04cb-ff5d-7148-a3a4a09087e0' receipt_handle='tieorwmmbmddkzcnnafvdnjgqyfrxlxcqkiayjhutldwdbtdczctghhfojgujgjdnherzxgxlbwxhncauzzflcqjyjwxueiaqwbwzuobmohlzsrtrlpxtgmwrtmcwuqfqpfdzqiyedbjrzukmutwjedwnidxpfrgdtwioegdopgsavmtvacqgenag' attributes=None deleted=False uuid='a4749fe5-5cee-4e56-8b01-57d640220459' message='This is message 1'
Sleeping for 10.0 seconds to simulate long running work
Deleting task: message_id='247d9197-4d05-560e-1b41-11f117c90386' receipt_handle='yljrdcddjhlyxkzdkythukhmmlwdsnksojriqpbfjhnrecmzzxiqjtyilovkicqfpgtuazhhdbkvrkcnxeupypcjbroaiagkznwqwakpflwzbbnncnikvsrjrrvnqezyqnfvdpmzzskoncxkcqperrgbvqpylawdtjtmqgtytzcpvfdigdrwyfxwk' attributes=None deleted=False uuid='ff23c113-ac04-4534-a54b-cc9cc43122a8' message='This is message 2'
Deleting task: message_id='a788e6d9-51be-66d6-51f3-7d4f65aaa538' receipt_handle='wnoxchcqwsvrjlhapuafwwqqjfumbkttqagdqpzkyqakpfgikfrggcfwefxsnhvooaealkihtqlrbjjrkdkqrgszitycabxwsvbbaocevigazabzowrbaefnitlxxabmeicxxocfvpjdgiuorqtxigriatrupqrlxyzipfhzhdjsxipjyquiruoqi' attributes=None deleted=False uuid='eeca0cbe-7bba-41db-b63c-9fe91350739d' message='This is message 3'
Sleeping for 10.0 seconds to simulate long running work
Deleting task: message_id='7388fcce-1946-fb50-f135-a37785f2dc2e' receipt_handle='qwziqrviwzgpgiyrvrdwdjtnbmpuyrfmjekrazleedsbjwclxscadqbgavxkgazxnrzexuhkxhpzwzffpktnxqgizscrahbdabyyjienommuqnjrdoxlqzcrauepfrfsnsyczdwvmrkgasortxyaexerdqpisqmckvnifucmvdbljzyycebiayxcj' attributes=None deleted=False uuid='96759e7d-a2a5-41b3-8a66-7545fc521efd' message='This is message 4'
Deleting task: message_id='1af54a6f-fb64-c620-6ae1-18ca53c2cacc' receipt_handle='nwlcdoklxgynygzyziekmkvwlxjeaijiylpihjrjgnklyrzevfprlfbdnbhruxcpcsgxxhbwosxmybcwjvgydpxrgahyyzrwzaldidcfakudocrvsnjxljulpyaaaanpwkbuhxdrmvncuxnblfegwnqqwikmlntokdbhhzabsocwlfpusmvutdeco' attributes=None deleted=False uuid='7cbb41f4-2a54-4cf5-80ac-0d964b8ee766' message='This is message 5'
Sleeping for 10.0 seconds to simulate long running work
Deleting task: message_id='1c4362c4-2931-776d-73b2-92c6c4e0ee51' receipt_handle='wjhmjbqclbcgwwseftzscsoixguydvtzjadlwuileqictbaesbhcvxadszyykxzvpytiopjiqigaytlnmkbxqwjqelgefrccjakrjwqnspotrqytugjwmiirkdxqjdjtyccpfaxgmdwmdpvnalfngpsvabmwavwulekmkkorsesbyizqkmgxfxsra' attributes=None deleted=False uuid='16a6af41-7224-415a-9052-6ddf8b58870b' message='This is message 6'
Deleting task: message_id='e26bd6ee-a886-fbe0-5370-329300e099b0' receipt_handle='hxnpwrslqgjfbngkaufoiiwgflxjisozpdfudosbiumsgfvahdxtloukeeiwswuzsqdnotwicmmedmqlimckvvqjjxmhxbtuapyiwdsakshjiiqsroqnsvicypwqgtaxjngdjehtlszozgkguiaeepzuwyunfcyiklgpbfgaxmrkqqkveekhvpjnj' attributes=None deleted=False uuid='4f77dd16-a9ce-4d1a-aa24-607de6e0218e' message='This is message 7'
Sleeping for 10.0 seconds to simulate long running work
Deleting task: message_id='d57c8109-75be-a963-5c10-16ef7f4de514' receipt_handle='swjgwvblyiursbwrpgwzkffzsikaypucvbqoleemxyhjqdtrghyifyquyfuwchbykzvtnvuwoujsaktfpwflzpnltksusvjqdlpkepverfbdywrvmvenrmmplumfunpecqndeffpuasnlkbtnpcgmzvaezeumuuwxaggkttolzryjfuiogajqduoy' attributes=None deleted=False uuid='6ac9df84-1c81-4ba5-9cd2-a313dc12ce5f' message='This is message 8'
Deleting task: message_id='626212b4-acca-13c2-0e05-8619ff432649' receipt_handle='txhxnlvoosxiddlqgoibfzusdroapotvauhxmaosxxstvfrobdowydkvpwqzugqioafdotyvksuarvcckuohqstxjmxdcuchtsifbvhydtcdxhciehcvxvehpzvzofyycbhvgavoxhsbwixmvgxoarxviqmqwnonydworxutiuiisewoldfnhibil' attributes=None deleted=False uuid='f7ae1210-cb0b-450f-bf64-cc64b8de7eb6' message='This is message 9'
Sleeping for 10.0 seconds to simulate long running work
Deleting task: message_id='c08ca4f8-46b2-8788-0bc3-36a47369cd53' receipt_handle='jxedhtsahyqlnzljrzezbktowxnwycdjiyiawyxtrnrxkfmntvetdatmxbojfnihmlkaidymczezzzqddpyryfaevqpyfgbgtzcofwjbkqiabolizjmodffjencwyvbkgxxmcvqmttbllvzigwudrtsmyuiaefjvkqufchcqmioqxnfgsqggjqjqw' attributes=None deleted=False uuid='89c8187d-bf8e-4ee1-be90-faccb474a08c' message='This is message 10'
Deleting task: message_id='d0e8f62d-c30c-1d1f-8bb9-ee702a776c33' receipt_handle='djiymcanhkpyjitjkyocopigtcuhqhelswycrkcxztaycurlihinuqrlpgtkrpthtdudnavoxwbyohenohpvwmhaxeldbujtpxfbtzixclbvhllvotmyeimwzkphddfonanfmxmzdhskwuscdxgmkpidzrwxhynzavhyuebhjsywjoyokjbkhktaa' attributes=None deleted=False uuid='2b279610-2a81-4eb1-8984-247814009a26' message='This is message 11'
Sleeping for 10.0 seconds to simulate long running work
No tasks found, sleeping 1.0 before polling again
No tasks found, sleeping 1.0 before polling again
No tasks found, sleeping 1.0 before polling again
No tasks found, sleeping 1.0 before polling again
```

You can kill the worker with Ctrl-C
