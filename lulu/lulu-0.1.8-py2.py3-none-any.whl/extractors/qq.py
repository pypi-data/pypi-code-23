#!/usr/bin/env python

import re
import json

from lulu.util import log
from lulu.extractors.qie import download as qieDownload
from lulu.extractors.qie_video import download_by_url as qie_video_download
from lulu.common import (
    match1,
    matchall,
    url_info,
    print_info,
    get_content,
    url_locations,
    download_urls,
    playlist_not_supported,
)


__all__ = ['qq_download']
site_info = 'QQ.com'


def qq_download_by_vid(
    vid, title, output_dir='.', merge=True, info_only=False
):
    info_api = (
        'http://vv.video.qq.com/getinfo?otype=json&appver=3.2.19.333'
        '&platform=11&defnpayver=1&vid={}'.format(vid)
    )
    info = get_content(info_api)
    video_json = json.loads(match1(info, r'QZOutputJson=(.*)')[:-1])
    fn_pre = video_json['vl']['vi'][0]['lnk']
    title = video_json['vl']['vi'][0]['ti']
    host = video_json['vl']['vi'][0]['ul']['ui'][0]['url']
    streams = video_json['fl']['fi']
    seg_cnt = video_json['vl']['vi'][0]['cl']['fc']
    if seg_cnt == 0:
        seg_cnt = 1

    # best_quality = streams[-1]['name']
    part_format_id = streams[-1]['id']

    part_urls = []
    total_size = 0
    for part in range(1, seg_cnt+1):
        filename = '{}.p{}.{}.mp4'.format(
            fn_pre, str(part_format_id % 10000), str(part)
        )
        key_api = (
            'http://vv.video.qq.com/getkey?otype=json&platform=11&'
            'format={}&vid={}&filename={}&appver=3.2.19.333'.format(
                part_format_id, vid, filename
            )
        )
        part_info = get_content(key_api)
        key_json = json.loads(match1(part_info, r'QZOutputJson=(.*)')[:-1])
        if key_json.get('key') is None:
            vkey = video_json['vl']['vi'][0]['fvkey']
            url = '{}{}?vkey={}'.format(
                video_json['vl']['vi'][0]['ul']['ui'][0]['url'],
                fn_pre + '.mp4',
                vkey
            )
        else:
            vkey = key_json['key']
            url = '{}{}?vkey={}'.format(host, filename, vkey)
        if not vkey:
            if part == 1:
                log.wtf(key_json['msg'])
            else:
                log.w(key_json['msg'])
            break

        part_urls.append(url)
        _, ext, size = url_info(url)
        total_size += size

    print_info(site_info, title, ext, total_size)
    if not info_only:
        download_urls(
            part_urls, title, ext, total_size, output_dir=output_dir,
            merge=merge
        )


def kg_qq_download_by_shareid(
    shareid, output_dir='.', info_only=False, caption=False
):
    BASE_URL = 'http://cgi.kg.qq.com/fcgi-bin/kg_ugc_getdetail'
    params_str = (
        '?dataType=jsonp&jsonp=callback&jsonpCallback=jsopgetsonginfo&'
        'v=4&outCharset=utf-8&shareid={}'.format(shareid)
    )
    url = BASE_URL + params_str
    content = get_content(url)
    json_str = content[len('jsonpcallback('):-1]
    json_data = json.loads(json_str)

    playurl = json_data['data']['playurl']
    videourl = json_data['data']['playurl_video']
    real_url = playurl if playurl else videourl
    real_url = real_url.replace('\/', '/')

    ksong_mid = json_data['data']['ksong_mid']
    lyric_url = (
        'http://cgi.kg.qq.com/fcgi-bin/fcg_lyric?jsonpCallback=jsopgetlrcdata&'
        'outCharset=utf-8&ksongmid={}'.format(ksong_mid)
    )
    lyric_data = get_content(lyric_url)
    lyric_string = lyric_data[len('jsopgetlrcdata('):-1]
    lyric_json = json.loads(lyric_string)
    lyric = lyric_json['data']['lyric']

    title = match1(lyric, r'\[ti:([^\]]*)\]')

    type, ext, size = url_info(real_url)
    if not title:
        title = shareid

    print_info('腾讯全民K歌', title, type, size)
    if not info_only:
        download_urls([real_url], title, ext, size, output_dir, merge=False)
        if caption:
            caption_filename = title + '.lrc'
            caption_path = output_dir + '/' + caption_filename
            with open(caption_path, 'w') as f:
                lrc_list = lyric.split('\r\n')
                for line in lrc_list:
                    f.write(line)
                    f.write('\n')


def qq_download(url, output_dir='.', merge=True, info_only=False, **kwargs):
    if re.match(r'https?://egame.qq.com/live\?anchorid=(\d+)', url):
        from . import qq_egame
        qq_egame.qq_egame_download(
            url, output_dir=output_dir, merge=merge, info_only=info_only,
            **kwargs
        )
        return

    if 'kg.qq.com' in url or 'kg2.qq.com' in url:
        shareid = url.split('?s=')[-1]
        caption = kwargs['caption']
        kg_qq_download_by_shareid(
            shareid, output_dir=output_dir, info_only=info_only,
            caption=caption
        )
        return

    if 'live.qq.com' in url:
        if 'live.qq.com/video/v' in url:
            qie_video_download(
                url, output_dir=output_dir, merge=merge, info_only=info_only,
                **kwargs
            )
        else:
            qieDownload(
                url, output_dir=output_dir, merge=merge, info_only=info_only
            )
        return

    if 'mp.weixin.qq.com/s?' in url:
        content = get_content(url)
        vids = matchall(content, [r'\?vid=(\w+)'])
        for vid in vids:
            qq_download_by_vid(vid, vid, output_dir, merge, info_only)
        return

    # do redirect
    if 'v.qq.com/page' in url:
        # for URLs like this:
        # http://v.qq.com/page/k/9/7/k0194pwgw97.html
        new_url = url_locations([url])[0]
        if url == new_url:
            # redirect in js?
            content = get_content(url)
            url = match1(content, r'window\.location\.href="(.*?)"')
        else:
            url = new_url

    if 'kuaibao.qq.com' in url or re.match(
        r'http://daxue.qq.com/content/content/id/\d+', url
    ):
        content = get_content(url)
        vid = match1(content, r'vid\s*=\s*"\s*([^"]+)"')
        title = match1(content, r'title">([^"]+)</p>')
        title = title.strip() if title else vid
    elif 'iframe/player.html' in url:
        vid = match1(url, r'\bvid=(\w+)')
        # for embedded URLs; don't know what the title is
        title = vid
    else:
        content = get_content(url)
        # vid = parse_qs(urlparse(url).query).get('vid')
        # for links specified vid like
        # http://v.qq.com/cover/p/ps6mnfqyrfo7es3.html?vid=q0181hpdvo5
        rurl = match1(
            content, r'<link.*?rel\s*=\s*"canonical".*?href\s*="(.+?)".*?>'
        )  # https://v.qq.com/x/cover/9hpjiv5fhiyn86u/t0522x58xma.html
        vid = ''
        if rurl:
            vid = rurl.split('/')[-1].split('.')[0]
        if vid == 'undefined':
            vid = ''
        # https://v.qq.com/x/cover/ps6mnfqyrfo7es3/q0181hpdvo5.html?
        vid = vid if vid else url.split('/')[-1].split('.')[0]
        # general fallback
        vid = vid if vid else match1(content, r'vid"*\s*:\s*"\s*([^"]+)"')
        if not vid:
            vid = match1(content, r'id"*\s*:\s*"(.+?)"')
        title = match1(
            content, r'<a.*?id\s*=\s*"{}".*?title\s*=\s*"(.+?)".*?>'.format(
                vid
            )
        )
        title = match1(content, r'title">([^"]+)</p>') if not title else title
        title = match1(content, r'"title":"([^"]+)"') if not title else title
        title = vid if not title else title  # general fallback

    qq_download_by_vid(vid, title, output_dir, merge, info_only)


download = qq_download
download_playlist = playlist_not_supported(site_info)
