import asyncio
import json
import sys
from typing import Optional, Dict, Any

# Import the Twitter class and related functions from twitter.py
from twitter import Twitter, to_json, UserNotFound

class UserStatsChecker:
    def __init__(self, auth_token: str, ct0: str = "", proxy: str = ""):
        """
        Initialize the UserStatsChecker with authentication tokens.
        
        Args:
            auth_token: Twitter auth_token from browser cookies
            ct0: Twitter ct0 token from browser cookies (optional, will be fetched if not provided)
            proxy: Proxy URL (optional)
        """
        # Create a mock AccountInfo object since we don't have the full models
        class MockAccountInfo:
            def __init__(self, auth_token, ct0, proxy):
                self.twitter_auth_token = auth_token
                self.twitter_ct0 = ct0
                self.proxy = proxy
                self.twitter_error = False
        
        self.account_info = MockAccountInfo(auth_token, ct0, proxy)
        self.twitter_client = Twitter(self.account_info)
    
    async def initialize(self):
        """Initialize the Twitter client."""
        try:
            await self.twitter_client.start()
            print(f"✅ Berhasil login sebagai: @{self.twitter_client.my_username}")
            return True
        except Exception as e:
            print(f"❌ Gagal login: {str(e)}")
            return False
    
    async def get_user_stats(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive statistics for a Twitter user.
        
        Args:
            username: Twitter username (with or without @)
            
        Returns:
            Dictionary containing user statistics or None if user not found
        """
        try:
            # Clean username
            if username.startswith('@'):
                username = username[1:]
            
            print(f"🔍 Mencari data untuk @{username}...")
            
            # Get user ID first
            user_id = await self.twitter_client.get_user_id(username)
            
            # Get followers count
            followers_count = await self.twitter_client.get_followers_count(username)
            
            # Get user tweets and replies
            tweets_data = await self._get_user_tweets_and_replies(user_id, username)
            
            stats = {
                'username': username,
                'user_id': user_id,
                'followers_count': followers_count,
                'tweets_count': tweets_data.get('tweets_count', 0),
                'replies_count': tweets_data.get('replies_count', 0),
                'total_posts': tweets_data.get('total_posts', 0),
                'recent_tweets': tweets_data.get('recent_tweets', [])
            }
            
            return stats
            
        except UserNotFound:
            print(f"❌ User @{username} tidak ditemukan atau akun private")
            return None
        except Exception as e:
            print(f"❌ Error saat mengambil data @{username}: {str(e)}")
            return None
    
    async def _get_user_tweets_and_replies(self, user_id: str, username: str) -> Dict[str, Any]:
        """
        Get user's tweets and replies using the UserTweets API.
        
        Args:
            user_id: Twitter user ID
            username: Twitter username
            
        Returns:
            Dictionary with tweet and reply counts
        """
        action = "UserTweets"
        query_id = "E3opETHurmVJflFsUBVuUQ"
        
        params = {
            'variables': to_json({
                "userId": user_id,
                "count": 100,  # Get more tweets for better accuracy
                "includePromotedContent": False,
                "withQuickPromoteEligibilityTweetFields": False,
                "withVoice": False,
                "withV2Timeline": True,
            }),
            'features': to_json({
                "profile_label_improvements_pcf_label_in_post_enabled": False,
                "rweb_tipjar_consumption_enabled": True,
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "premium_content_api_read_enabled": False,
                "communities_web_enable_tweet_community_results_fetch": True,
                "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "responsive_web_grok_analyze_button_fetch_trends_enabled": True,
                "responsive_web_grok_analyze_post_followups_enabled": False,
                "responsive_web_grok_share_attachment_enabled": False,
                "articles_preview_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "responsive_web_twitter_article_tweet_consumption_enabled": True,
                "tweet_awards_web_tipping_enabled": False,
                "creator_subscriptions_quote_tweet_preview_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "rweb_video_timestamps_enabled": True,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "responsive_web_enhance_cards_enabled": False,
            }),
        }
        
        url = f'https://x.com/i/api/graphql/{query_id}/{action}'
        
        def _handler(resp):
            instructions = resp['data']['user']['result']['timeline_v2']['timeline']['instructions']
            entries = None
            for instruction in instructions:
                if instruction['type'] == 'TimelineAddEntries':
                    entries = instruction['entries']
                    break
            
            if entries is None:
                return {'tweets_count': 0, 'replies_count': 0, 'total_posts': 0, 'recent_tweets': []}
            
            tweets_count = 0
            replies_count = 0
            recent_tweets = []
            
            for entry in entries:
                if 'tweet_results' not in entry.get('content', {}).get('itemContent', {}):
                    continue
                
                tweet_data = entry['content']['itemContent']['tweet_results']['result']
                if 'legacy' not in tweet_data:
                    continue
                
                legacy = tweet_data['legacy']
                tweet_text = legacy.get('full_text', '')
                in_reply_to_user_id = legacy.get('in_reply_to_user_id_str')
                
                # Extract tweet ID
                tweet_id = entry['entryId']
                if tweet_id.startswith('tweet-'):
                    tweet_id = tweet_id[6:]
                
                tweet_url = f'https://x.com/{username}/status/{tweet_id}'
                
                recent_tweets.append({
                    'id': tweet_id,
                    'text': tweet_text[:100] + '...' if len(tweet_text) > 100 else tweet_text,
                    'url': tweet_url,
                    'is_reply': bool(in_reply_to_user_id and in_reply_to_user_id != user_id)
                })
                
                # Count tweets vs replies
                if in_reply_to_user_id and in_reply_to_user_id != user_id:
                    replies_count += 1
                else:
                    tweets_count += 1
            
            return {
                'tweets_count': tweets_count,
                'replies_count': replies_count,
                'total_posts': tweets_count + replies_count,
                'recent_tweets': recent_tweets[:10]  # Keep only 10 most recent
            }
        
        return await self.twitter_client.request('GET', url, params=params, resp_handler=_handler)

async def main():
    """Main function to run the user stats checker."""
    print("🐦 Twitter User Stats Checker")
    print("=" * 40)
    
    # Get authentication tokens from user
    print("\n📝 Masukkan informasi autentikasi Twitter:")
    auth_token = input("Auth Token (dari browser cookies): ").strip()
    ct0 = input("CT0 Token (dari browser cookies, optional): ").strip()
    proxy = input("Proxy URL (optional): ").strip()
    
    if not auth_token:
        print("❌ Auth Token diperlukan!")
        return
    
    # Initialize checker
    checker = UserStatsChecker(auth_token, ct0, proxy)
    
    # Initialize connection
    print("\n🔄 Menghubungkan ke Twitter...")
    if not await checker.initialize():
        return
    
    # Main loop
    while True:
        print("\n" + "=" * 40)
        print("📊 Menu:")
        print("1. Cek statistik user")
        print("2. Cek multiple users")
        print("3. Keluar")
        
        choice = input("\nPilih menu (1-3): ").strip()
        
        if choice == "1":
            username = input("Masukkan username Twitter (dengan atau tanpa @): ").strip()
            if username:
                stats = await checker.get_user_stats(username)
                if stats:
                    print(f"\n📊 Statistik @{stats['username']}:")
                    print(f"   👥 Followers: {stats['followers_count']:,}")
                    print(f"   🐦 Tweets: {stats['tweets_count']}")
                    print(f"   💬 Replies: {stats['replies_count']}")
                    print(f"   📝 Total Posts: {stats['total_posts']}")
                    
                    if stats['recent_tweets']:
                        print(f"\n🕒 10 Tweet Terbaru:")
                        for i, tweet in enumerate(stats['recent_tweets'], 1):
                            type_icon = "💬" if tweet['is_reply'] else "🐦"
                            print(f"   {i}. {type_icon} {tweet['text']}")
                            print(f"      🔗 {tweet['url']}")
        
        elif choice == "2":
            usernames_input = input("Masukkan usernames (pisahkan dengan koma): ").strip()
            usernames = [u.strip() for u in usernames_input.split(',') if u.strip()]
            
            if usernames:
                print(f"\n📊 Mengecek {len(usernames)} users...")
                results = []
                
                for username in usernames:
                    stats = await checker.get_user_stats(username)
                    if stats:
                        results.append(stats)
                        print(f"✅ @{username}: {stats['tweets_count']} tweets, {stats['replies_count']} replies")
                    else:
                        print(f"❌ @{username}: Gagal mengambil data")
                
                if results:
                    print(f"\n📋 Ringkasan:")
                    print(f"{'Username':<20} {'Followers':<12} {'Tweets':<8} {'Replies':<8} {'Total':<8}")
                    print("-" * 60)
                    for stats in results:
                        print(f"{'@'+stats['username']:<20} {stats['followers_count']:<12,} {stats['tweets_count']:<8} {stats['replies_count']:<8} {stats['total_posts']:<8}")
        
        elif choice == "3":
            print("👋 Sampai jumpa!")
            break
        
        else:
            print("❌ Pilihan tidak valid!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Program dihentikan oleh user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}") 