

def test_utils():
    import utils
    
    # dict_updater test
    dicts = {'d1':{'name': 'foo', 'age':18}, 'd2':{'name': 'steve', 'gender':'male'}}
    dicts['d3'] = dicts['d1'].copy()
    dicts['d3'].update(dicts['d2'])
    assert utils.dict_updater(dicts['d1'], dicts['d2']) == dicts['d3']
    
    # metric_size_formatter test
    increase = lambda x:x*1024
    data = {1024: '1.00 KB', 1024*1024: '1.00 MB', 1024*1024*1024: '1.00 GB', 1024*1024*1024*1024: '1.00 TB'}
    for value, to_match in data.items():
        assert utils.metric_size_formatter(value, suffix='B', decimal_places=2) == to_match, "metric_size_formatter returns incorrect string representation for '{} == {}'".format('metric_size_formatter({}, suffix=\'B\', decimal_places=2)'.format(value), to_match)
    
    # get_date_from_string test
    valid_dates = ['22-04-07', '2022-04-07', '22/04/07', '2022/04/07', '22.04.07', '2022.04.07', '22 04 07', '2022 04 07', '07-04-22', '07-04-2022', '07/04/22', '07/04/2022', '07.04.22', '07.04.2022', '07 04 22', '07 04 2022', '070422', '07042022']
    invalid_dates = ['22', '04', '07']
    for entry in valid_dates:
        assert utils.get_date_from_string(entry) is not None
    for entry in invalid_dates:
        assert utils.get_date_from_string(entry) is None
    
    # remove_duplicate_in_list test
    max_id = 100
    max_sub_id = 5
    dataset_generator = lambda id, sub_id: {'id':id, 'sub_id': sub_id}
    dataset = [[dataset_generator(_id+1, sub_id+1) for sub_id in range(max_sub_id)] for _id in range(max_id)]
    flatten_dataset = [entry for _set in dataset for entry in _set]
    cleaned_dataset = utils.remove_duplicate_in_list(flatten_dataset, 'id', lambda entry:entry['sub_id'])
    assert cleaned_dataset == [{'id':_id+1, 'sub_id': max_sub_id} for _id in range(max_id)]


# TODO: make test cases for other modules
