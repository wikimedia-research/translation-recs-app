import os, system
langs  = sys.argv[1].split(',')



os.system("export HIVE_OPTS='-hiveconf mapreduce.job.queuename=priority'")


for lang in langs:
    params = {'lang': lang}

    
    create_query = """
    CREATE TABLE  prod_tables.%(lang)swiki_redirect_joined (
    rd_from STRING,
    rd_to STRING)
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY '\t'
    STORED AS TEXTFILE;
    set mapreduce.job.queuename=priority;
    INSERT OVERWRITE TABLE prod_tables.%(lang)swiki_redirect_joined
    SELECT 
    b.page_title as rd_from,
    a.rd_title as rd_to
    FROM prod_tables.%(lang)swiki_redirect a JOIN prod_tables.%(lang)swiki_page b ON( a.rd_from = b.page_id);
    """


    cmd =  """hive -e " """ +create_query % params + """ " """
    print (cmd)
    os.system( cmd )



    create_query = """
    CREATE TABLE  prod_tables.%(lang)swiki_langlinks_joined (
    ll_from STRING,
    ll_to STRING,
    ll_lang STRING)
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY '\t'
    STORED AS TEXTFILE;
    set mapreduce.job.queuename=priority;
    INSERT OVERWRITE TABLE prod_tables.%(lang)swiki_langlinks_joined
    SELECT 
    b.page_title as ll_from,
    a.ll_title as ll_to,
    a.ll_lang as ll_lang
    FROM prod_tables.%(lang)swiki_langlinks a JOIN prod_tables.%(lang)swiki_page b ON( a.ll_from = b.page_id);
    """


    cmd =  """hive -e " """ +create_query % params + """ " """
    print (cmd)
    os.system( cmd )





