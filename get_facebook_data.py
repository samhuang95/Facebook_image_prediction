import json, requests, time
from datetime import datetime, timedelta
from connect_to_sql import SQLCommand
from urllib.request import urlretrieve

target_fanpage_id = 'TARGET FANPAGE ID'
fanpage_access_token = 'YOUR FANPAGE ACCESS TOKEN'

def get_insights(data: dict) -> list:
  insights_dict = {insights_data['name']: insights_data['values'][0]['value'] for insights_data in data}

  insights_dict['post_impressions_by_story_type'] = insights_dict['post_impressions_by_story_type']['other'] if 'other' in insights_dict['post_impressions_by_story_type'] else 0
  insights_dict['post_impressions_by_story_type_unique'] = insights_dict['post_impressions_by_story_type_unique']['other'] if 'other' in insights_dict['post_impressions_by_story_type_unique'] else 0
  
  insights_dict['post_negative_feedback_by_type_hide_all_clicks'] = insights_dict['post_negative_feedback_by_type']['hide_all_clicks'] if 'hide_all_clicks' in insights_dict['post_negative_feedback_by_type'] else 0
  insights_dict['post_negative_feedback_by_type_hide_clicks'] = insights_dict['post_negative_feedback_by_type']['hide_clicks'] if 'hide_clicks' in insights_dict['post_negative_feedback_by_type'] else 0
  insights_dict['post_negative_feedback_by_type_unique_hide_all_clicks'] = insights_dict['post_negative_feedback_by_type_unique']['hide_all_clicks'] if 'hide_all_clicks' in insights_dict['post_negative_feedback_by_type_unique'] else 0
  insights_dict['post_negative_feedback_by_type_unique_hide_clicks'] = insights_dict['post_negative_feedback_by_type_unique']['hide_clicks'] if 'hide_clicks' in insights_dict['post_negative_feedback_by_type_unique'] else 0

  insights_dict['post_clicks_by_type_other_clicks'] = insights_dict['post_clicks_by_type']['other clicks'] if 'other clicks' in insights_dict['post_clicks_by_type'] else 0
  insights_dict['post_clicks_by_type_photo_view'] = insights_dict['post_clicks_by_type']['photo view'] if 'photo view' in insights_dict['post_clicks_by_type'] else 0
  insights_dict['post_clicks_by_type_link_clicks'] = insights_dict['post_clicks_by_type']['link clicks'] if 'link clicks' in insights_dict['post_clicks_by_type'] else 0
  insights_dict['post_clicks_by_type_unique_other_clicks'] = insights_dict['post_clicks_by_type_unique']['other clicks'] if 'other clicks' in insights_dict['post_clicks_by_type_unique'] else 0
  insights_dict['post_clicks_by_type_unique_photo_view'] = insights_dict['post_clicks_by_type_unique']['photo view'] if 'photo view' in insights_dict['post_clicks_by_type_unique'] else 0
  insights_dict['post_clicks_by_type_unique_link_clicks'] = insights_dict['post_clicks_by_type_unique']['link clicks'] if 'link clicks' in insights_dict['post_clicks_by_type_unique'] else 0

  insights_dict['post_reactions_by_type_total_like'] = insights_dict['post_reactions_by_type_total']['like'] if 'like' in insights_dict['post_reactions_by_type_total'] else 0
  insights_dict['post_reactions_by_type_total_love'] = insights_dict['post_reactions_by_type_total']['love'] if 'love' in insights_dict['post_reactions_by_type_total'] else 0
  insights_dict['post_reactions_by_type_total_wow'] = insights_dict['post_reactions_by_type_total']['wow'] if 'wow' in insights_dict['post_reactions_by_type_total'] else 0
  insights_dict['post_reactions_by_type_total_haha'] = insights_dict['post_reactions_by_type_total']['haha'] if 'haha' in insights_dict['post_reactions_by_type_total'] else 0
  insights_dict['post_reactions_by_type_total_sorry'] = insights_dict['post_reactions_by_type_total']['sorry'] if 'sorry' in insights_dict['post_reactions_by_type_total'] else 0
  insights_dict['post_reactions_by_type_total_anger'] = insights_dict['post_reactions_by_type_total']['anger'] if 'anger' in insights_dict['post_reactions_by_type_total'] else 0
  
  del insights_dict['post_impressions_by_story_type']
  del insights_dict['post_impressions_by_story_type_unique']
  del insights_dict['post_negative_feedback_by_type']
  del insights_dict['post_negative_feedback_by_type_unique']
  del insights_dict['post_clicks_by_type']
  del insights_dict['post_clicks_by_type_unique']
  del insights_dict['post_reactions_by_type_total']
  
  return list(insights_dict.values())

def get_tags(data: dict, post_id: str) -> None:
  if 'message_tags' in data:
    values = []
    for tag in data['message_tags']: values.append(str((post_id, tag['name'])))
    values_string = ','.join(values)
    SQLCommand().modify(f'INSERT INTO tags (post_id, text) VALUES {values_string}')

def get_photos(data: dict, post_id: str) -> None:
  if 'attachments' in data:
    values = []
    post_attachment = data['attachments']['data'][0]
    photo = post_attachment['media']['image']['src']
    if 'external' not in photo: values.append(str((post_id, photo)))
    if 'subattachments' in data['attachments']['data'][0]:
      for image in data['attachments']['data'][0]['subattachments']['data'][1:]:
        photo = image['media']['image']['src']
        if 'external' not in photo: values.append(str((post_id, photo)))
    values_string = ','.join(values)
    SQLCommand().modify(f'INSERT INTO photos (post_id, url) VALUES {values_string}')

def get_comments(data: dict, post_id: str) -> None:
  if 'comments' in data:
    values = []
    for comment in data['comments']['data']:
      comment_id = comment['id'].split('_')[1]
      comment_time = comment['created_time'].replace('T', ' ').split('+')[0]
      values.append(str((post_id, comment_id, comment_time, comment['message'])))
    values_string = ','.join(values)
    SQLCommand().modify(f'INSERT INTO comments (post_id, comment_id, time, text) VALUES {values_string}')

def get_post_data(fanpage_id: str, fanpage_access_token: str) -> None:
  fields = 'posts.limit(50){id,created_time,is_popular,message,message_tags,shares{count},attachments{media{image{src}},subattachments{media{image{src}}}},comments.summary(total_count),insights.metric(post_impressions,post_impressions_unique,post_impressions_fan,post_impressions_fan_unique,post_impressions_viral,post_impressions_viral_unique,post_impressions_nonviral,post_impressions_nonviral_unique,post_impressions_by_story_type,post_impressions_by_story_type_unique,post_engaged_users,post_negative_feedback,post_negative_feedback_unique,post_negative_feedback_by_type,post_negative_feedback_by_type_unique,post_engaged_fan,post_clicks,post_clicks_unique,post_clicks_by_type,post_clicks_by_type_unique,post_reactions_by_type_total),likes.summary(total_count),reactions.summary(total_count)}'
  url = f'https://graph.facebook.com/{fanpage_id}?fields={fields}&access_token={fanpage_access_token}'

  response = requests.get(url)
  data = response.json()['posts'] if 'posts' in response.json() else response.json()

  for post_data in data['data']:
    post_id = post_data['id'].split('_')[1]
    if SQLCommand().get(f'SELECT id FROM posts WHERE id = {post_id}'): continue

    post_time = post_data['created_time'].replace('T', ' ').split('+')[0]
    if (datetime.utcnow() - datetime.strptime(post_time, '%Y-%m-%d %H:%M:%S')).days < 7: continue

    post_text = post_data['message'] if 'message' in post_data else ''

    post_likes = post_data['likes']['summary']['total_count']
    post_reactions = post_data['reactions']['summary']['total_count']
    post_shares = post_data['shares']['count'] if 'shares' in post_data else 0
    post_comments = post_data['comments']['summary']['total_count']
    post_popular = post_data['is_popular']
    
    values_string = str(tuple([post_id, post_time, post_text, post_likes, post_reactions, post_shares, post_comments, post_popular] + get_insights(post_data['insights']['data'])))
    SQLCommand().modify(f'INSERT INTO posts (id, time, text, likes, reactions, shares, comments, popular, post_impressions, post_impressions_unique, post_impressions_fan, post_impressions_fan_unique, post_impressions_viral, post_impressions_viral_unique, post_impressions_nonviral, post_impressions_nonviral_unique, post_engaged_users, post_negative_feedback, post_negative_feedback_unique, post_engaged_fan, post_clicks, post_clicks_unique, post_negative_feedback_by_type_hide_all_clicks, post_negative_feedback_by_type_hide_clicks, post_negative_feedback_by_type_unique_hide_all_clicks, post_negative_feedback_by_type_unique_hide_clicks, post_clicks_by_type_other_clicks, post_clicks_by_type_photo_view, post_clicks_by_type_link_clicks, post_clicks_by_type_unique_other_clicks, post_clicks_by_type_unique_photo_view, post_clicks_by_type_unique_link_clicks, post_reactions_by_type_total_like, post_reactions_by_type_total_love, post_reactions_by_type_total_wow, post_reactions_by_type_total_haha, post_reactions_by_type_total_sorry, post_reactions_by_type_total_anger) VALUES {values_string}')
    
    get_tags(post_data, post_id)
    get_photos(post_data, post_id)
    get_comments(post_data, post_id)

def get_fanpage_data(fanpage_id: str, fanpage_access_token: str) -> None:
  fanpage_data_dict = {}
  fields = 'insights.metric(page_content_activity_by_action_type_unique,page_content_activity_by_age_gender_unique,page_content_activity_by_city_unique,page_content_activity_by_country_unique,page_content_activity_by_locale_unique,page_content_activity,page_content_activity_by_action_type,post_activity,post_activity_unique,post_activity_by_action_type,post_activity_by_action_type_unique,page_impressions,page_impressions_unique,page_impressions_paid,page_impressions_paid_unique,page_impressions_organic_v2,page_impressions_organic_unique_v2,page_impressions_viral,page_impressions_viral_unique,page_impressions_nonviral,page_impressions_nonviral_unique,page_impressions_by_story_type,page_impressions_by_story_type_unique,page_impressions_by_city_unique,page_impressions_by_country_unique,page_impressions_by_locale_unique,page_impressions_by_age_gender_unique,page_impressions_frequency_distribution,page_impressions_viral_frequency_distribution,page_engaged_users,page_post_engagements,page_consumptions,page_consumptions_unique,page_consumptions_by_consumption_type,page_consumptions_by_consumption_type_unique,page_places_checkin_total,page_places_checkin_total_unique,page_places_checkin_mobile,page_places_checkin_mobile_unique,page_places_checkins_by_age_gender,page_places_checkins_by_locale,page_places_checkins_by_country,page_negative_feedback,page_negative_feedback_unique,page_negative_feedback_by_type,page_negative_feedback_by_type_unique,page_positive_feedback_by_type,page_positive_feedback_by_type_unique,page_fans_online_per_day,page_fan_adds_by_paid_non_paid_unique,page_actions_post_reactions_like_total,page_actions_post_reactions_love_total,page_actions_post_reactions_wow_total,page_actions_post_reactions_haha_total,page_actions_post_reactions_sorry_total,page_actions_post_reactions_anger_total,page_actions_post_reactions_total,page_total_actions,page_cta_clicks_logged_in_total,page_cta_clicks_logged_in_unique,page_cta_clicks_by_site_logged_in_unique,page_cta_clicks_by_age_gender_logged_in_unique,page_cta_clicks_logged_in_by_country_unique,page_cta_clicks_logged_in_by_city_unique,page_call_phone_clicks_logged_in_unique,page_call_phone_clicks_by_age_gender_logged_in_unique,page_call_phone_clicks_logged_in_by_country_unique,page_call_phone_clicks_logged_in_by_city_unique,page_call_phone_clicks_by_site_logged_in_unique,page_get_directions_clicks_logged_in_unique,page_get_directions_clicks_by_age_gender_logged_in_unique,page_get_directions_clicks_logged_in_by_country_unique,page_get_directions_clicks_logged_in_by_city_unique,page_get_directions_clicks_by_site_logged_in_unique,page_website_clicks_logged_in_unique,page_website_clicks_by_age_gender_logged_in_unique,page_website_clicks_logged_in_by_country_unique,page_website_clicks_logged_in_by_city_unique,page_website_clicks_by_site_logged_in_unique,page_fans,page_fans_locale,page_fans_city,page_fans_country,page_fans_gender_age,page_fan_adds,page_fan_adds_unique,page_fans_by_like_source,page_fans_by_like_source_unique,page_fan_removes,page_fan_removes_unique,page_fans_by_unlike_source_unique,page_tab_views_login_top_unique,page_tab_views_login_top,page_tab_views_logout_top,page_views_total,page_views_logout,page_views_logged_in_total,page_views_logged_in_unique,page_views_external_referrals,page_views_by_profile_tab_total,page_views_by_profile_tab_logged_in_unique,page_views_by_internal_referer_logged_in_unique,page_views_by_site_logged_in_unique,page_views_by_age_gender_logged_in_unique,page_views_by_referers_logged_in_unique)'
  url = f'https://graph.facebook.com/{fanpage_id}?fields={fields}&access_token={fanpage_access_token}'

  insights_data = requests.get(url).json()['insights']['data']
  for metric in insights_data:
    if metric['name'] not in fanpage_data_dict: fanpage_data_dict[metric['name']] = {}
    if metric['period'] not in fanpage_data_dict[metric['name']]:
      fanpage_data_dict[metric['name']][metric['period']] = metric['values'][-1]['value']

  date = (datetime.utcnow() - timedelta(days=2)).strftime('%m%d')
  
  with open(f'fanpage_data/fanpage_data_{date}.json', 'w', encoding='utf-8') as f:
    json.dump(fanpage_data_dict, f, indent=2, ensure_ascii=False)

def get_photos_data(fanpage_id: str, fanpage_access_token: str) -> None:
  fields = 'posts.limit(50){id,created_time,message,attachments{media{image{src}},subattachments{media{image{src}}}},insights.metric(post_impressions,post_impressions_unique,post_clicks_by_type)}'
  url = f'https://graph.facebook.com/{fanpage_id}?fields={fields}&access_token={fanpage_access_token}'

  photo_dict = {}
  while url:
    response = requests.get(url)

    if not response.json().get('posts') and not response.json().get('data'):
      time.sleep(10)
      continue

    data = response.json()['posts'] if 'posts' in response.json() else response.json()
    for post_data in data['data']:
      post_id = post_data['id'].split('_')[1]
      post_time = post_data['created_time'].replace('T', ' ').split('+')[0]
      post_text = post_data['message'] if 'message' in post_data else ''
      post_impressions_unique = post_data['insights']['data'][1]['values'][0]['value']
      post_photo_view = post_data['insights']['data'][2]['values'][0]['value']['photo view'] if 'photo view' in post_data['insights']['data'][2]['values'][0]['value'] else 0

      if (datetime.utcnow() - datetime.strptime(post_time, '%Y-%m-%d %H:%M:%S')).days < 7: continue
      if datetime.strptime(post_time, '%Y-%m-%d %H:%M:%S') < datetime.strptime('2021-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'): break
      if '中獎' in post_text or '得獎' in post_text or '獲獎' in post_text or '徵才' in post_text or '抽獎' in post_text or '報名' in post_text or '名額' in post_text or '活動' in post_text: continue
      
      i = 1
      if 'attachments' in post_data:
        photo_url = post_data['attachments']['data'][0]['media']['image']['src']
        if 'external' not in photo_url:
          try: urlretrieve(photo_url, f'photos/{post_id}_{i}.jpg')
          except: print(post_id, photo_url)
          i += 1
        if 'subattachments' in post_data['attachments']['data'][0][1:]:
          for photo in post_data['attachments']['data'][0]['subattachments']['data']:
            photo_url = photo['media']['image']['src']
            if 'external' not in photo_url:
              try: urlretrieve(photo_url, f'photos/{post_id}_{i}.jpg')
              except: print(post_id, photo_url)
              i += 1

      photo_dict[post_id] = {
        'time': post_time,
        'impressions_unique': post_impressions_unique,
        'photo_views': post_photo_view
      }

    url = data['paging'].get('next')

  with open('photo_data.json', 'w', encoding='utf-8') as f:
    json.dump(photo_dict, f, indent=2, ensure_ascii=False)

if __name__ == 'main':
  pass
