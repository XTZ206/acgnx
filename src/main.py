import argparse
import handlers, view
from subjects import Subject


def main():
    apihandler = handlers.APIHandler()
    dbhandler = handlers.DBHandler("acgnx.db")

    argparser = argparse.ArgumentParser(
        prog="acgnx", usage="%(prog)s [command]", description="ACGN indeX v0.0.1"
    )
    subparsers = argparser.add_subparsers(dest="command")
    
    list_parser = subparsers.add_parser("list", help="list subjects")
    view_parser = subparsers.add_parser("view", help="view subject with id")
    view_parser.add_argument("id", type=int, help="view subject with id")
    view_parser.add_argument("-f", "--fetch", action="store_true", help="fetch subject before viewing")
    view_parser.add_argument("-c", "--count", type=int, help="count of infobox items to show", default=5)
    update_parser = subparsers.add_parser("update", help="update subjects")
    fetch_parser = subparsers.add_parser("fetch", help="fetch subjects")
    fetch_parser.add_argument("id", type=int, help="fetch subject with id")
    search_parser = subparsers.add_parser("search", help="search subjects with name")
    search_parser.add_argument("keyword", type=str, help="search keyword")
    search_parser.add_argument("--online", action="store_true", help="search subjects from bgm.tv")
    search_parser.add_argument("--store", action="store_true", help="store search results to database")

    args = argparser.parse_args()
    
    match args.command:
        
        case "list":
            viewer = view.Viewer(dbhandler.fetch_all_subjects())
            viewer.list_subjects()
            return

        case "view":

            if args.fetch:
                viewer = view.Viewer([Subject(id=args.id)], view.Updater(apihandler))
                viewer.update_subjects()
                dbhandler.insert_subjects(viewer.subjects)
            else:
                viewer = view.Viewer([Subject(id=args.id)], view.Updater(dbhandler))
                viewer.update_subjects()
            viewer.view_subject(viewer.subjects[0], args.count)
            return

        case "update":
            viewer = view.Viewer(dbhandler.fetch_all_subjects(), view.Updater(apihandler))
            viewer.update_subjects()
            dbhandler.update_subjects(viewer.subjects)
            viewer.list_subjects()
            print("All subjects updated")
            return

        case "fetch":
            viewer = view.Viewer([Subject(id=args.id)], view.Updater(apihandler))
            viewer.update_subjects()
            dbhandler.insert_subjects(viewer.subjects)
            return              

        case "search":
            
            updater = view.Updater(apihandler) if args.online else view.Updater(dbhandler)
            viewer = view.Viewer([], updater, view.Selector())
            viewer.search_subjects(args.keyword)
            viewer.list_subjects()
            if args.store:
                dbhandler.insert_subjects(viewer.subjects)
            print("Viewing search results")
            return
            

        case _:
            argparser.print_help()
            return          


if __name__ == "__main__":
    main()
