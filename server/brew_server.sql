SQLite format 3   @   ��                                                               �� -�   �    �                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                ` ����`@  ����`@  ����`@   � � � � `                              :32017-03-15 02:53:56@P��ڹ�Z932017-03-15 02:53:44@P��ڹ�Z832017-03-15 02:53:32@P��ڹ�Z732017-03-15 02:53:20@P~fffff632017-03-15 02:53:08@P~fffff532017-03-15 02:52:56@P~fffff432017-03-15 02:52:44@P~fffff332017-03-15 02:52:32@Pw$tS��232017-03-15 02:52:20@Pw$tS��132017-03-15 02:52:08@Pw$tS��032017-03-15 02:51:56@Pw$tS��/32017-03-15 02:51:45@Pw$tS��.32017-03-15 02:51:33@Pp     -32017-03-15 02:51:21@Pp     ,32017-03-15 02:51:09@Pp     +32017-03-15 02:50:57@Pp     *32017-03-15 02:50:45@Ph��(�)32017-03-15 02:50:32@Pp     (32017-03-15 02:50:20@Ph��(�'32017-03-15 02:50:08@Ph��(�&32017-03-15 02:49:57@Ph��(�%32017-03-15 02:49:45@Ph��(�$32017-03-15 02:49:33@Ph��(�#32017-03-15 02:49:21@Ph��(�"32017-03-15 02:49:09@Ph��(�!32017-03-15 02:48:57@Ph��(� 32017-03-15 02:48:46@Pa�����32017-03-15 02:48:34@Pa�����32017-03-15 02:48:22@Ph��(�    ` ����`@  ����`@  ����`@   � � � � `                              W32017-03-15 02:59:44@P������V32017-03-15 02:59:32@P������U32017-03-15 02:59:20@P������T32017-03-15 02:59:08@P������S32017-03-15 02:58:56@P������R32017-03-15 02:58:44@P������Q32017-03-15 02:58:32@P������P32017-03-15 02:58:20@P�W���'O32017-03-15 02:58:08@P�W���'N32017-03-15 02:57:56@P�W���'M32017-03-15 02:57:44@P�W���'L32017-03-15 02:57:32@P�W���'K32017-03-15 02:57:20@P�W���'J32017-03-15 02:57:08@P�33333I32017-03-15 02:56:56@P�33333H32017-03-15 02:56:44@P�33333G32017-03-15 02:56:32@P�33333F32017-03-15 02:56:20@P��A [�E32017-03-15 02:56:08@P��A [�D32017-03-15 02:55:56@P��A [�C32017-03-15 02:55:45@P��A [�B32017-03-15 02:55:33@P������A32017-03-15 02:55:21@P��A [�@32017-03-15 02:55:08@P������?32017-03-15 02:54:56@P������>32017-03-15 02:54:44@P������=32017-03-15 02:54:32@P������<32017-03-15 02:54:20@P��ڹ�Z;32017-03-15 02:54:08@P��ڹ�Z   � �                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      Cider 2

   � �                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
	Cider 2   � �                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           9-!32 Minute Warning@@2017-03-162017-03-16 02:34:23
   � �                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  -	2 Minute Warning                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 	 4 ]. 4�g�� �                          �D�otablekegkegCREATE TABLE keg(
  name text primary key,
  current_volume integer not null,
  total_volume integer not null
, tap_date date, last_pour_volume integer, last_pour_time datetime)�4�GtableyeastyeastCREATE TABLE yeast(
  name text primary key,
  type text not null,
  starter_vol float not null,
  starter_dme float not null,
  vol_pitched float not null
)'
; indexsqlite_autoindex_hops_1hops�		�utablehopshops
CREATE TABLE hops(
  name text primary key,
  type text not null,
  amount float not null,
  minutes text not null
))= indexsqlite_autoindex_grain_1grain	s�EtablegraingrainCREATE TABLE grain(
  name text primary key,
  type text not null,
  amount float not null
)%9 indexsqlite_autoindex_keg_1keg-A indexsqlite_autoindex_bottles_1bottles� �tablebottlesbottlesCREATE TABLE bottles(
  name text primary key,
  num_bottles_12oz integer not null,
  num_bottles_22oz integer not null
, id integer)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  ���� ��Z 5                               �                                                                                                                   �&�+tablebrewsbrewsCREATE TABLE "brews"(
  name text primary key,
  style text not null,
  brew_date date not null,
  in_bottles integer not null,
  on_tap integer not null,
  fermenting integer not null
, description text, og text, fg text, abv text, ibu text, id integer, style_type text))= indexsqlite_autoindex_brews_1brews W�tablechamberchamber CREATE TABLE chamber(set_temp int, avg float, set_range int)v%%�/tabletemperaturestemperaturesCREATE TABLE temperatures(timestamp datetime not null,temperature float not null)'; indexsqlite_autoindex_mash_1mash�W�tablemashmashCREATE TABLE mash(
  name text primary key,
  pre_boil_vol float,
  strike_temp integer,
  mash_temp integer,
  mash_time integer,
  OG text,
  FG text,
  ABV float,
  vol_into_fermenter float
))= indexsqlite_autoindex_yeast_1yeast                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 �    ��������                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           �h   �K   �.   �   t   W   :       ` ����`@  ����`@  ����`@   � � � � `                              32017-03-15 02:48:10@Ph��(�32017-03-15 02:47:58@Pa�����32017-03-15 02:47:46@Pa�����32017-03-15 02:47:35@Ph��(�32017-03-15 02:47:23@Ph��(�32017-03-15 02:47:11@Ph��(�32017-03-15 02:46:59@Pp     32017-03-15 02:46:47@Ph��(�32017-03-15 02:46:36@Pp     32017-03-15 02:46:24@Pp     32017-03-15 02:46:12@Pp     32017-03-15 02:46:00@Pw$tS��32017-03-15 02:45:48@Pw$tS��32017-03-15 02:45:36@Pw$tS��32017-03-15 02:15:25@Qk�A [�32017-03-14 17:20:15@Q2W���'32017-03-14 17:19:58@Q2W���'32017-03-14 17:19:41@Q2W���'32017-03-14 17:19:29@Q2W���'
32017-03-14 17:19:04@Q2W���'	32017-03-14 17:18:53@Q2W���'32017-03-14 17:18:31@Q2W���'32017-03-14 17:18:19@Q2W���'32017-03-14 17:17:56@Q+3333332017-03-14 17:17:13@Q2W���'32017-03-14 16:47:12@Q2W���'32017-03-14 16:46:29@Q2W���'32017-03-14 16:46:13@Q2W���'32017-03-14 16:45:49@Q2W���'   �    ���                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
� � �����I��f�}U���(;                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     -2 Minute WarningCitra IPA-Belgian Pale Ale+Belgian Trippel5Stone Pale Ale Clone!GKona Coffee and Vanilla Stout#IPAutin Boh)Tropical WheatWhite IPACider 1
%Hoppy Saison	1Denoggonizer CloneCGreat Lakes Chillwave Clone%Brown Porter)Dunkelweizen 1%American IPA#Irish Red 1�     Cider 2   
          ` ����`@  ����`@  ����`@   � � � � `                              t32017-03-15 03:05:34@P�fffffs32017-03-15 03:05:22@P�fffffr32017-03-15 03:05:10@P�fffffq32017-03-15 03:04:58@P�fffffp32017-03-15 03:04:46@P�fffffo32017-03-15 03:04:34@P�fffffn32017-03-15 03:04:23@P�fffffm32017-03-15 03:04:11@P�$tS��l32017-03-15 03:03:59@P�$tS��k32017-03-15 03:03:47@P�fffffj32017-03-15 03:03:35@P�$tS��i32017-03-15 03:03:23@P�$tS��h32017-03-15 03:03:12@P�fffffg32017-03-15 03:03:00@P�$tS��f32017-03-15 03:02:48@P�$tS��e32017-03-15 03:02:36@P�$tS��d32017-03-15 03:02:24@P�$tS��c32017-03-15 03:02:12@P�$tS��b32017-03-15 03:02:01@P�     a32017-03-15 03:01:49@P�     `32017-03-15 03:01:37@P�     _32017-03-15 03:01:25@P�     ^32017-03-15 03:01:13@P�     ]32017-03-15 03:00:56@P���(�\32017-03-15 03:00:44@P�     [32017-03-15 03:00:32@P���(�Z32017-03-15 03:00:20@P���(�Y32017-03-15 03:00:08@P���(�X32017-03-15 02:59:56@P������    N ����`@  ���^=����wV5 � � � � o N            �32017-03-15 03:11:20@P��A [��32017-03-15 03:11:08@P��A [��32017-03-15 03:10:56@P��A [��32017-03-15 03:10:44@P��A [��32017-03-15 03:10:32@P��A [��32017-03-15 03:10:20@P��A [��32017-03-15 03:10:08@P��A [��
32017-03-15 03:09:56@P�������	32017-03-15 03:09:44@P�������32017-03-15 03:09:32@P��A [��32017-03-15 03:09:20@P�������32017-03-15 03:09:08@P�������32017-03-15 03:08:56@P�������32017-03-15 03:08:44@P�������32017-03-15 03:08:32@P�������32017-03-15 03:08:21@P�������32017-03-15 03:08:09@P������� 32017-03-15 03:07:57@P������32017-03-15 03:07:45@P͊ڹ�Z~32017-03-15 03:07:33@P͊ڹ�Z}32017-03-15 03:07:21@P͊ڹ�Z|32017-03-15 03:07:10@P͊ڹ�Z{32017-03-15 03:06:58@P͊ڹ�Zz32017-03-15 03:06:45@P͊ڹ�Zy32017-03-15 03:06:33@P͊ڹ�Zx32017-03-15 03:06:21@P�fffffw32017-03-15 03:06:09@P͊ڹ�Zv32017-03-15 03:05:57@P͊ڹ�Zu32017-03-15 03:05:46@P�fffff    J ���|[:����tS2����lK* � � � � k J        �.32017-03-15 07:57:52@Q#�
=p��-32017-03-15 07:42:42@Q������,32017-03-15 07:27:40@Q������+32017-03-15 07:12:29@Q������*32017-03-15 06:57:18@Qz�G��)32017-03-15 06:42:07@Q
=p���(32017-03-15 06:26:55D�'32017-03-15 06:11:45@P���R�&32017-03-15 05:56:33@P�33333�%32017-03-15 05:41:31@P�fffff�$32017-03-15 05:26:20@Pw
=p���#32017-03-15 05:11:08@P��Q��"32017-03-15 04:56:05@Q9������!32017-03-15 04:40:55@Q2�\(��� 32017-03-15 04:25:45@Q*�G�{�32017-03-15 04:10:34@Q#�
=p��32017-03-15 03:55:23@Q������32017-03-15 03:40:12@Qz�G��32017-03-15 03:25:00@P��\)�32017-03-15 03:17:12@P�W���'�32017-03-15 03:16:27@P�W���'�32017-03-15 03:12:56@P�33333�32017-03-15 03:12:44@P�33333�32017-03-15 03:12:32@P�33333�32017-03-15 03:12:20@P��A [��32017-03-15 03:12:08@P��A [��32017-03-15 03:11:56@P��A [��32017-03-15 03:11:44@P��A [��32017-03-15 03:11:32@P��A [�    �  ��
Q�                                                                                                                                                                                                                              �M-!	�/ 	2 Minute WarningIPA2016-10-31IPA brewed with Mosaic, Citra and Amarillo hops boiled for only 2 minutes giving this beer a lot of hop flavor and aroma without much bitterness.1.0696.952IPA/PA�%!�%Brown PorterPorter2015-04-12Brown Porter with American Cascade hops. First beer with yeast starter.1.0581.0106.240Stout/Porter�6)%!�iDunkelweizen 1Dunkelweizen2015-03-22Dark wheat beer with traditional german Saaz hops. First beer with fermentation chamber and first beer kegged.1.0501.0105.220Wheat� %!�American IPAIPA2015-02-22Standard American IPA with Cascade hops. First BIAB all grain beer1.0581.0106.285IPA/PAq#!�Irish Red 1Irish Red2015-01-22First beer brewed. Used an extract kit from Northern Brewer5.0Other    m @g� m                                                                                           �,#!�_White IPASession IPA2015-08-16Session IPA made with 30% white wheat malt. Brewed with citra and cascade hops, and a hoppy water profile1.0451.0104.555IPA/PA�
!�YCider 1Cider2015-08-04Dry Cider made with organic apple cider. Ended up tasting light evethough high ABV. For Meg obviously.1.0781.0049.80
Cider�&	%!�M#Hoppy SaisonSaison2015-07-26Saison made with lots of German Saaz hops. First beer made with custom water profile - balanced.1.0501.0105.250	Belgian Ale�V1!�1Denoggonizer CloneIPA2015-05-31Clone of Drakes Denoggonizer double IPA. Lots of chinook and Cascade hops at the end of fermentation and dry hop. This beer turned out very bitter1.0651.0107.295IPA/PA�=C!�mGreat Lakes Chillwave CloneIPA2015-04-25Clone of Great Lakes Chillwave double IPA. Lots of Citra and Cascade hops balanced out with honey malt sweetness1.0551.0105.975IPA/PA�  � ; �^ �                                                                                                                                                                �+#!�iIPAutin BohIPA2015-09-26IPA brewed when Autin Boh visited. Lots of Citra and Amarillo late and dry hops. Made with Hoppy water profile1.0511.0105.365IPA/PA�/G!�=%Kona Coffee and Vanilla StoutStout2015-11-15Stout brewed with Thunder Mountain Kona Coffee cold brew and vanilla beans from Mountain View farmers market.  Made with a malty water profile and German Hops. Bottles were overcarbonated and caused some bottle bombs1.0651.0107.243Stout/Porter   �                                                                                                                                                                       �B)!�Tropical WheatWheat2015-09-13Tropical Wheat beer made with 3 mangos, 2 papayas and cascade hops. Balanced water profile. First beer made with electric kettle.1.0481.0105.020Wheatk  � {�} �                                                                                                                                                                                                                                     �!�Citra IPAIPA2016-07-09IPA brewed with lots of Citra and Cascade Hops with a 30 minute hop rest1.0701.0176.959IPA/PA�++!�#Belgian TrippelBelgian Trippel2016-10-04Belgian Trippel made with German Hops and Belgian Ardennes yeast1.0831.0089.538Belgian Ale�4!	�Cider 2Cider2015-11-20Cider made with organic apple cider from the Mountain View Farmers Market. No sugar added, so lower ABV. For Meg obviously.1.0421.0045.00Cider�--!�##Belgian Pale AleBelgian Pale Ale2016-05-15Belgian Pale Ale made per request by my mother. It is now her favorite beer1.0601.0106.233Belgian Ale               �5!}Stone Pale Ale ClonePale Ale2016-01-16Stone Pale Ale clone made per request by Meg's Mom Cathy1.0541.0214.542IPA/PA    J ���|[:����tS2����sR1 � � � � k J        �K32017-03-15 15:17:22@Q\(��J32017-03-15 15:02:21@Qz�G��I32017-03-15 14:47:10@Qz�G��H32017-03-15 14:31:58@Qz�G��G32017-03-15 14:16:47@Qz�G��F32017-03-15 14:01:36@Q\(��E32017-03-15 13:46:25@Qz�G��D32017-03-15 13:31:21@Qz�G��C32017-03-15 13:16:10@Qz�G��B32017-03-15 13:01:00@Q
=p���A32017-03-15 12:45:49@Q
=p���@32017-03-15 12:30:39@Q
=p���?32017-03-15 12:15:37@Q
=p���>32017-03-15 12:00:26@Q
=p���=32017-03-15 11:45:15D�<32017-03-15 11:30:03@P��\)�;32017-03-15 11:14:51@P���R�:32017-03-15 10:59:39@P�33333�932017-03-15 10:44:27@P��Q��832017-03-15 10:29:16@P�������732017-03-15 10:14:05@Pa��R�632017-03-15 09:59:03@Q������532017-03-15 09:43:52@Q9������432017-03-15 09:28:41@Q9������332017-03-15 09:13:30@Q2�\(���232017-03-15 08:58:18@Q2�\(���132017-03-15 08:43:07@Q2�\(���032017-03-15 08:27:55@Q*�G�{�/32017-03-15 08:12:53@Q*�G�{    C ���|[:����tS2����lK*	 � � � � d C �h32017-03-15 22:36:39@Q#�
=p��g32017-03-15 22:21:34@Q#�
=p��f32017-03-15 22:06:31@Q������e32017-03-15 21:51:21@Q������d32017-03-15 21:36:09@Q������c32017-03-15 21:20:58@Q\(��b32017-03-15 21:05:48@Q\(��a32017-03-15 20:50:47@Q\(��`32017-03-15 20:35:34@Q\(��_32017-03-15 20:20:32@Q\(��^32017-03-15 20:05:22@Q\(��]32017-03-15 19:50:11@Qz�G��\32017-03-15 19:35:00@Qz�G��[32017-03-15 19:19:50@Qz�G��Z32017-03-15 19:04:39@Qz�G��Y32017-03-15 18:49:29@Qz�G��X32017-03-15 18:34:17@Qz�G��W32017-03-15 18:19:06@Qz�G��V32017-03-15 18:03:54@Qz�G��U32017-03-15 17:48:52@Qz�G��T32017-03-15 17:33:51@Qz�G��S32017-03-15 17:18:39@Qz�G��R32017-03-15 17:03:28@Qz�G��Q32017-03-15 16:48:18@Qz�G��P32017-03-15 16:33:07@Q\(��O32017-03-15 16:17:57@Q\(��N32017-03-15 16:02:46@Q\(��M32017-03-15 15:47:44@Q\(��L32017-03-15 15:32:32@Q\(�   2 ���|[:����tS2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              �v32017-03-16 02:08:48@Q9������u32017-03-16 01:53:46@Q9������t32017-03-16 01:38:35@Q2�\(���s32017-03-16 01:23:23@Q9������r32017-03-16 01:08:12@Q2�\(���q32017-03-16 00:53:02@Q2�\(���p32017-03-16 00:37:51@Q2�\(���o32017-03-16 00:22:41@Q2�\(���n32017-03-16 00:07:31@Q*�G�{�m32017-03-15 23:52:18@Q*�G�{�l32017-03-15 23:37:07@Q#�
=p��k32017-03-15 23:21:54@Q#�
=p��j32017-03-15 23:06:53@Q#�
=p��i32017-03-15 22:51:50@Q#�
=p�   � �                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      D@Qz�G�