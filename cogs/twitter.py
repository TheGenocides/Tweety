import discord
import pytweet
from discord.ext import commands
from typing import Union

class Twitter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command('user', description="A command for user lookup")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def userLookup(self, ctx, username: Union[str, int]):
        try:
            user=None

            if username.isdigit():
                user=self.bot.twitter.fetch_user(username)
            
            else:
                user = self.bot.twitter.fetch_user_by_username(username)
            await ctx.send(
                embed=discord.Embed(
                    title=user.name,
                    url=user.profile_link,
                    description=f":link: {user.link if len(user.link) > 0 else '*This user doesnt provide link*'} | <:compas:879722735377469461> {user.location}\n{user.bio if len(user.bio) > 0 else '*User doesnt provide a bio*'}",
                    color=discord.Color.blue(),
                )
                .set_author(
                    name=user.username + f"({user.id})",
                    icon_url=user.avatar_url,
                    url=user.profile_link,
                )
                .set_footer(
                    text=f"Created Time: {user.created_at.strftime('%Y/%m/%d')}",
                    icon_url=user.avatar_url,
                )
                .add_field(
                    name="Followers",
                    value=user.follower_count
                )
                .add_field(
                    name="Following",
                    value=user.following_count
                )
                .add_field(
                    name="Tweets",
                    value=user.tweet_count
                )
                .add_field(
                    name="Listed",
                    value=user.listed_count
                )
            )

        except pytweet.errors.NotFoundError:
            await ctx.send(f"Could not find user with username(or id): [{username}].")

    @commands.command('tweet', description="A command for tweet lookup")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tweetLookup(self, ctx, tweet_id: int):
        try:
            tweet = self.bot.twitter.fetch_tweet(tweet_id)
            user = tweet.author
            em=discord.Embed(
                title=f"Posted by {user.name}",
                url=tweet.link,
                description=tweet.text,
                color=discord.Color.blue()
            ).set_author(
                name=user.username + f"({user.id})",
                icon_url=user.avatar_url,
                url=user.profile_link
            ).set_footer(
                text=f"{tweet.created_at.strftime('%Y/%m/%d')} | {tweet.source} | Reply: {tweet.reply_setting}",
                icon_url=user.avatar_url
            ).add_field(
                name="Likes Count 👍", 
                value=tweet.like_count
            ).add_field(
                name="Quotes Count 📰", 
                value=tweet.quote_count
            ).add_field(
                name="Replies Count 🗨️", 
                value=tweet.reply_count
            ).add_field(
                name="Retweetes Count 🗨️", 
                value=tweet.retweet_count
            )
        

            if tweet.embeds:
                em.set_image(
                    url=tweet.embeds[0].images[0].url
                )

            await ctx.send(
                embed=em
            )

            if tweet.poll:
                await ctx.send(
                    "looks like this tweet has a poll, mind checking that out with `e!poll <tweet_id>`?"
                )

        except pytweet.errors.NotFoundError:
            await ctx.send(f"Could not find user with username(or id): [{tweet_id}].")
    
    @commands.command('poll', description="See a tweet's poll")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def poll(self, ctx, tweet_id: int):
        try:
            tweet = self.bot.twitter.fetch_tweet(tweet_id)
            user = tweet.author
            if not tweet.poll:
                return await ctx.send("That tweet doesnt have poll")

            em=discord.Embed(
                title=f"Poll for tweet({tweet.id})",
                url=tweet.link,
                description="",
                color=discord.Color.blue()
            ).set_author(
                name=user.username + f"({user.id})",
                icon_url=user.avatar_url,
                url=user.profile_link
            ).set_footer(
                text=f"Duration: {tweet.poll.duration} Seconds | Poll Open: {tweet.poll.voting_status}"
            )

            for option in tweet.poll.options:
                em.description += f"**Option {option.position}**\n. . .**Label:** {option.label}\n. . .**Votes:** {option.votes}\n\n"
            await ctx.send(embed=em)

        except pytweet.errors.NotFoundError:
            await ctx.send("Tweet not found!")

    @commands.command("follow",description="Follow a user, only the bot owners can do this")
    @commands.is_owner()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def followUser(self, ctx, username: str):
        try:
            user = None
            me = self.bot.twitter.user
            if username.isdigit():
                user = self.bot.twitter.fetch_user(int(username))

            else:
                user = self.bot.twitter.fetch_user_by_username(username)

            user.follow()
            await ctx.send(f"{me.username} Has followed {user.username}!")

        except Exception as error:
            if isinstance(error, pytweet.errors.NotFoundError):
                await ctx.send(f"Could not find user with username(or id): [{username}].")
            else:
                raise error

    @commands.command("unfollow", description="UnFollow a user, only the bot owners can do this")
    @commands.is_owner()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def unfollowUser(self, ctx, username: str):
        try:
            user = None
            me = self.bot.twitter.user
            if username.isdigit():
                user = self.bot.twitter.fetch_user(int(username))

            else:
                user = self.bot.twitter.fetch_user_by_username(username)

            user.unfollow()
            await ctx.send(f"{me.username} Has unfollowed {user.username}!")

        except Exception as error:
            if isinstance(error, pytweet.errors.NotFoundError):
                await ctx.send(f"Could not find user with username(or id): [{username}].")
                
            else:
                raise error

    @commands.command("following", description="Return users that i followed")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def Clientfollowing(self, ctx):
        users=self.bot.twitter.user.following
        txt=""
        for num, user in enumerate(users):
            txt += f"{num + 1}. {user.username}({user.id})\n"
        
        await ctx.send(f"Here are **{len(users)}** cool people i followed!\n{txt}")

    @commands.command("send", description="Send a message to a user, only owner of the bot can do this!")
    @commands.is_owner()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def sendMessagetoUser(self, ctx, username: Union[str, int], *, text: str):
        user = None
        if username.isdigit():
            user = self.bot.twitter.fetch_user(int(username))

        else:
            user = self.bot.twitter.fetch_user_by_username(username)

        user.send(text)
        await ctx.send(f"Send message to {user.username}")

    @commands.command("post", description="Post a tweet to twitter! only owner of the bot can do this!")
    @commands.is_owner()
    async def postTweet(self, ctx, *, text):
        tweet=None
        try:
            tweet=self.bot.twitter.tweet(text)
            await ctx.send(f"Posted! check it on {tweet.link}")
        except pytweet.Forbidden:
            await ctx.send(f"Posted! check it on {tweet.link}")

def setup(bot: commands.Bot):
    bot.add_cog(Twitter(bot))