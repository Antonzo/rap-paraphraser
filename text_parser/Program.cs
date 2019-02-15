using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Linq;
using System.Text;

namespace MUAM
{
    class Song
    {
        public string title, author, text;
    }

    class Program
    {
        static List<Song> songs = new List<Song>();
        static WebClient client = new WebClient();
        static List<string> error_log = new List<string>();

        static string FormatText(string text)
        {
            return text.Replace("<br />", " ").Replace("\n", "").Replace("&#039;", "'").Replace("«", "\"")
                        .Replace("&laquo;", "\"").Replace("&#8230;", "...").Replace("&nbsp;", " ")
                        .Replace("—", "-").Replace("&mdash;", "-").Replace("&raquo;", "\"").Replace("&#8212;", "-")
                        .Replace("&ldquo;", "\"").Replace("&rdquo;", "\"").Replace("&#8217;", "'")
                        .Replace("&#171;", "\"").Replace("&hellip;", "...").Replace("&lt;", "<").Replace("&gt;", ">")
                        .Replace("&amp;", "&").Replace("&#038;", "&").Replace("&#187;", "\"");
        }

        static void ParseLink(string link, int link_i)
        {
            string htmlCode;
            try
            {
                htmlCode = client.DownloadString(link).Replace("Текст песни &#8212;", "Текст песни");
                Song song = new Song();
                int pos1 = htmlCode.IndexOf("<h1 class=\"entry-title\">Текст песни ");

                int pos2 = htmlCode.IndexOf(" &#8212; ", pos1+1);
                int pos2_1 = htmlCode.IndexOf(" – ", pos1 + 1);
                if (pos2_1 < pos2 && pos2_1 != -1) pos2 = pos2_1;

                int pos3 = htmlCode.IndexOf("</h1>", pos2+1);

                if (pos1 == -1 || pos2 == -1 || pos3 == -1)
                {
                    Console.ForegroundColor = ConsoleColor.Red;
                    Console.WriteLine("Ошибка разбора кода ссылки #" + link_i);
                    Console.ForegroundColor = ConsoleColor.Gray;
                    return;
                }
                song.author = FormatText(htmlCode.Substring(pos1 + 36, pos2 - pos1 - 36));
                song.title = FormatText(htmlCode.Substring(pos2 + 9, pos3 - pos2 - 9));

                if (songs.Exists(x => x.author == song.author && x.title == song.title))
                {
                    Console.ForegroundColor = ConsoleColor.Yellow;
                    Console.WriteLine("Пропуск ссылки #" + link_i + ", песня " + song.title + " (" + song.author + ") уже обработана");
                    Console.ForegroundColor = ConsoleColor.Gray;
                    return;
                }

                int pos4 = htmlCode.IndexOf("<p>", pos3 + 1);
                int pos5 = htmlCode.IndexOf("</p>", pos4 + 1);
                if (pos4 == -1 || pos5 == -1)
                {
                    Console.ForegroundColor = ConsoleColor.Red;
                    Console.WriteLine("Ошибка разбора кода ссылки #" + link_i);
                    Console.ForegroundColor = ConsoleColor.Gray;
                    return;
                }
                string text = FormatText(htmlCode.Substring(pos4 + 3, pos5 - pos4 - 3));

                int pos6 = text.IndexOf('&');
                if (pos6 != -1 && text.IndexOf(';', pos6) != -1)
                {
                    int pos7 = text.IndexOf(';', pos6);
                    Console.ForegroundColor = ConsoleColor.Red;
                    Console.WriteLine("Ошибка разбора кода ссылки #" + link_i + ", не заменен html символ " + 
                        text.Substring(pos6, pos7 - pos6));
                    Console.ForegroundColor = ConsoleColor.Gray;
                    return;
                }

                song.text = text;
                songs.Add(song);
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("Ссылка #" + link_i + ", песня " + song.title + " (" + song.author + ") успешно обработана");
                Console.ForegroundColor = ConsoleColor.Gray;
            }
            catch (WebException)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("Ошибка загрузки ссылки #" + link_i);
                Console.ForegroundColor = ConsoleColor.Gray;
                return;
            }
            catch (Exception)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("Исключение при обработки ссылки #" + link_i);
                Console.ForegroundColor = ConsoleColor.Gray;
                return;
            }
        }

        static void Main(string[] args)
        {
            client.Encoding = Encoding.UTF8;
            string[] links = File.ReadAllLines("links.txt");
            Console.WriteLine("Всего ссылок в файле: " + links.Length);
            for (int i = 0; i < links.Length; i++) ParseLink(links[i], i+1);

            using (StreamWriter sw = File.CreateText("data.csv"))
            {
                foreach (var song in songs)
                {
                    sw.WriteLine("{0}|{1}|{2}", song.author, song.title, song.text);
                }
            }

            Console.ForegroundColor = ConsoleColor.Yellow;
            Console.WriteLine("Всего обработано песен: " + songs.Count);
            Console.ForegroundColor = ConsoleColor.Gray;
        }
    }
}
