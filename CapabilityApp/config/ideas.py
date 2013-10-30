        '''        
        sqlscript = ("SELECT * FROM process_step WHERE proc_step_id=%s", (proc_step_id))
        c = sql.DoCustomQueries()
        c.query(sqlscript)
        ddb_proc_step = c.results
        '''
        