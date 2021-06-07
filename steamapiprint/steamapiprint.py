#!/usr/bin/env python3

import os
import sys
import json
import argparse
import requests as req
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
section_group = parser.add_argument_group()
section_group.add_argument("--sections", help="Get all available sections", action='store_true')
api_group = parser.add_argument_group()
api_group.add_argument("--section", help="Use a section")
api_group_one = api_group.add_mutually_exclusive_group()
api_group_one.add_argument("--point", help="Show api for a point")
api_group_all = api_group.add_mutually_exclusive_group()
api_group_all.add_argument("--points", help="Show apis for all points", action='store_true')
api_group_names = api_group.add_mutually_exclusive_group()
api_group_names.add_argument("--point-names", help="Show all api point names", action='store_true')
api_export_group = parser.add_argument_group()
api_export_group.add_argument("--export", help="Export output to a file at path")
args = parser.parse_args()

if len(sys.argv[1:]) == 0:
    parser.print_help()
    sys.exit(0)

url = "https://partner.steamgames.com/doc/webapi"


def err(msg):
    print(msg)
    sys.exit()


def find(html, tag, params=None, all=True):
    soup = BeautifulSoup(html, "html.parser")
    if all:
        if params is None:
            return soup.findAll(tag)
        return soup.findAll(tag, params)
    if params is None:
        return soup.find(tag)
    return soup.find(tag, params)


def get_html(u):
    res = req.get(u, allow_redirects=False)

    if res.status_code != 200:
        err("Unable to access '{}'!".format(u))

    return res.text.strip()


def get_section(html):
    return find(html, "div", {"class": "docPageTitle"}, False).getText().split(" ")[0]


def get_titles(html):
    return find(html, "h2", {"class": "bb_section"})


def get_api_point(x):
    y = x.findNext("div", {"class": ["bb_code", "http", "hljs"]})

    point = y.getText().split(" ")
    return {"method": point[0], "url": point[1]}


def get_api_params(x):
    y = x.findNext("table")

    rows = y.findAll("tr")[1:]
    obj = {}
    for r in rows:
        tds = r.findAll("td")
        name = tds[0].getText()
        t = tds[1].getText()
        required = bool(tds[2].getText())
        description = tds[3].getText()
        obj[name] = {
            "type": t,
            "required": required,
            "description": description
        }
    return obj


def parse_api_point(title, aptx, apax):
    aptx["name"] = title if title is str else title.getText()
    aptx["params"] = apax
    return aptx


def get_api_for_title(title):
    api_point = get_api_point(title)
    api_params = get_api_params(title)
    return parse_api_point(title, api_point, api_params)


def get_points_for_section(x):
    y = get_html(url + "/" + x)
    titles = get_titles(y)

    apis = []
    for title in titles:
        apis.append(get_api_for_title(title))

    return apis


def get_point_names_for_section(x):
    y = get_html(url + "/" + x)
    return [x.getText() for x in get_titles(y)]


def get_point_for_title(x, p):
    y = get_html(url + "/" + x)
    titles = get_titles(y)

    for title in titles:
        if title.getText() == p:
            return get_api_for_title(title)

    return False


def get_all_sections():
    x = get_html(url)
    table = find(x, "table", None, False)
    return [sec.getText() for sec in table.select("td:first-child")]


def export(s, path):
    dirname = os.path.dirname(path) or os.getcwd()

    if os.path.exists(path):
        err("Can't write to already existing file!")
    elif os.access(dirname, os.W_OK):
        f = open(path, "w+")
        json.dump(s, f, indent=4)
        f.close()
        pass
    else:
        err("I can't write to this export path!")


def main():
    if args.sections:
        if args.export:
            export(get_all_sections(), args.export)
        else:
            for s in get_all_sections():
                print(s)
    elif args.section:
        if not args.point and not args.points and not args.point_names:
            err("Section argument needs --point or --points or --point-names argument!")
        elif args.point_names:
            if args.export:
                export(get_point_names_for_section(args.section), args.export)
            else:
                for s in get_point_names_for_section(args.section):
                    print(s)
        elif args.point:
            if args.export:
                export(get_point_for_title(args.section, args.point), args.export)
            else:
                print(get_point_for_title(args.section, args.point))
        elif args.points:
            if args.export:
                export(get_points_for_section(args.section), args.export)
            else:
                for s in get_points_for_section(args.section):
                    print(s)


if __name__ == "__main__":
    main()
