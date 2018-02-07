def dic_frame(multi_frame, end_dt, time_diff, func):
    # Add Max and Min
    dic_df = {}
    for td in time_diff:

        st_dt = shift_date(end_dt, td)
        idx_date = multi_frame.index.get_level_values(1)
        st_dt = nearest_valid_date(st_dt, idx_date)

        if func.upper() == 'D' or func.upper() == 'DIFF':
            dic_df[td] = biz.get_diff(multi_frame, st_dt, end_dt)

        elif func.upper() == 'P' or func.upper() == 'PERCENTILE':
            args = ('date', st_dt, end_dt, 'range')
            dic_df[td] = biz.get_percentile(multi_frame, end_dt, True, args)

        elif func.upper() == 'Z' or func.upper() == 'ZSCORE':
            args = ('date', st_dt, end_dt, 'range')
            dic_df[td] = biz.get_z_score(multi_frame, end_dt, True, args)

        elif func.upper() == 'S' or func.upper() == 'SURFACE':
            dic_df[td] = biz.get_surface(multi_frame, st_dt)

    return dic_df


def toggle_B(options, des='Relative time:', dis=False, b_style='', tips=None, styl={'button_width': '90px'}):
    if tips is None:
        tips = options
    tb = wg.ToggleButtons(
        options=options,
        description=des,
        disabled=dis,
        button_style=b_style,  # 'success', 'info', 'warning', 'danger' or ''
        tooltips=tips,
        style={'button_width': '90px'})
    return tb
