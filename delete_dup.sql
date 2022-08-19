delete   from WATCHES
where    rowid not in
         (
         select  min(rowid)
         from    WATCHES
         group by
                 model
         )