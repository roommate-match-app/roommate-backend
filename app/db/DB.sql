-- Схема БД сервиса «КакДостать Соседа» (PostgreSQL 16).
-- Сгенерировано из ORM-моделей app/db/models/models.py.
-- Источник истины — модели и миграции Alembic; файл носит справочный характер.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	role VARCHAR(10) DEFAULT 'user' NOT NULL, 
	is_blocked BOOLEAN DEFAULT FALSE NOT NULL, 
	registered_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	last_login TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT check_user_role CHECK (role IN ('user', 'admin')), 
	UNIQUE (email)
);

CREATE TABLE announcements (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	room_price INTEGER NOT NULL, 
	total_rooms INTEGER NOT NULL, 
	area INTEGER NOT NULL, 
	move_in_date DATE NOT NULL, 
	description TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	free BOOLEAN DEFAULT TRUE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT check_announcement_price CHECK (room_price >= 0), 
	CONSTRAINT check_announcement_rooms CHECK (total_rooms > 0), 
	CONSTRAINT check_announcement_area CHECK (area > 0), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE complaints (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	complainant_id UUID NOT NULL, 
	target_user_id UUID NOT NULL, 
	reason TEXT NOT NULL, 
	status VARCHAR(10) DEFAULT 'open' NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT check_complaint_status CHECK (status IN ('open', 'resolved', 'rejected')), 
	CONSTRAINT check_complaint_not_self CHECK (complainant_id <> target_user_id), 
	FOREIGN KEY(complainant_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(target_user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE favorites (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	target_type VARCHAR(12) NOT NULL, 
	target_id UUID NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT check_favorite_target CHECK (target_type IN ('profile', 'announcement')), 
	CONSTRAINT uq_favorites_user_target UNIQUE (user_id, target_type, target_id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE likes (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	from_user_id UUID NOT NULL, 
	to_user_id UUID NOT NULL, 
	liked_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT check_like_not_self CHECK (from_user_id <> to_user_id), 
	CONSTRAINT uq_likes_from_to UNIQUE (from_user_id, to_user_id), 
	FOREIGN KEY(from_user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(to_user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE matches (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user1_id UUID NOT NULL, 
	user2_id UUID NOT NULL, 
	matched_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT check_match_user_order CHECK (user1_id < user2_id), 
	CONSTRAINT uq_matches_user_pair UNIQUE (user1_id, user2_id), 
	FOREIGN KEY(user1_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(user2_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE notifications (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	type VARCHAR(20) NOT NULL, 
	body TEXT NOT NULL, 
	is_read BOOLEAN DEFAULT FALSE NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT check_notification_type CHECK (type IN ('like', 'match', 'message', 'application', 'review')), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE profiles (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	first_name VARCHAR(50) NOT NULL, 
	last_name VARCHAR(50) NOT NULL, 
	age INTEGER NOT NULL, 
	gender VARCHAR(10) NOT NULL, 
	city VARCHAR(100) NOT NULL, 
	district VARCHAR(100) NOT NULL, 
	metro_station VARCHAR(100) NOT NULL, 
	minutes_to_metro INTEGER, 
	bio TEXT, 
	photo_url TEXT, 
	PRIMARY KEY (id), 
	CONSTRAINT check_age CHECK (age >= 18 AND age <= 99), 
	CONSTRAINT check_gender CHECK (gender IN ('male', 'female')), 
	UNIQUE (user_id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE reviews (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	reviewer_id UUID NOT NULL, 
	reviewed_user_id UUID NOT NULL, 
	rating SMALLINT NOT NULL, 
	comment TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT check_review_rating CHECK (rating BETWEEN 1 AND 5), 
	CONSTRAINT check_review_not_self CHECK (reviewer_id <> reviewed_user_id), 
	CONSTRAINT uq_reviews_reviewer_reviewed UNIQUE (reviewer_id, reviewed_user_id), 
	FOREIGN KEY(reviewer_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(reviewed_user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE views (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	user_id UUID NOT NULL, 
	target_type VARCHAR(12) NOT NULL, 
	target_id UUID NOT NULL, 
	viewed_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT check_view_target CHECK (target_type IN ('profile', 'announcement')), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE addresses (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	announcement_id UUID NOT NULL, 
	city VARCHAR(100) NOT NULL, 
	street VARCHAR(150) NOT NULL, 
	house_number VARCHAR(10) NOT NULL, 
	district VARCHAR(100) NOT NULL, 
	metro_station VARCHAR(100) NOT NULL, 
	minutes_to_metro INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (announcement_id), 
	FOREIGN KEY(announcement_id) REFERENCES announcements (id) ON DELETE CASCADE
);

CREATE TABLE announcement_amenities (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	announcement_id UUID NOT NULL, 
	internet BOOLEAN DEFAULT FALSE NOT NULL, 
	furniture BOOLEAN DEFAULT FALSE NOT NULL, 
	kitchen BOOLEAN DEFAULT FALSE NOT NULL, 
	washing_machine BOOLEAN DEFAULT FALSE NOT NULL, 
	dishwasher BOOLEAN DEFAULT FALSE NOT NULL, 
	balcony BOOLEAN DEFAULT FALSE NOT NULL, 
	elevator BOOLEAN DEFAULT FALSE NOT NULL, 
	air_conditioning BOOLEAN DEFAULT FALSE NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (announcement_id), 
	FOREIGN KEY(announcement_id) REFERENCES announcements (id) ON DELETE CASCADE
);

CREATE TABLE announcement_photos (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	announcement_id UUID NOT NULL, 
	url TEXT NOT NULL, 
	is_main BOOLEAN DEFAULT FALSE NOT NULL, 
	position INTEGER DEFAULT 0 NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT check_photo_position CHECK (position >= 0), 
	FOREIGN KEY(announcement_id) REFERENCES announcements (id) ON DELETE CASCADE
);

CREATE TABLE announcement_rules (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	announcement_id UUID NOT NULL, 
	smoking_allowed BOOLEAN DEFAULT FALSE NOT NULL, 
	pets_allowed BOOLEAN DEFAULT FALSE NOT NULL, 
	guests_allowed BOOLEAN DEFAULT TRUE NOT NULL, 
	sleep_mode VARCHAR(10) DEFAULT 'any' NOT NULL, 
	noise_level VARCHAR(10) DEFAULT 'any' NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT check_announcement_sleep_mode CHECK (sleep_mode IN ('early', 'late', 'any')), 
	CONSTRAINT check_announcement_noise_level CHECK (noise_level IN ('quiet', 'loud', 'any')), 
	UNIQUE (announcement_id), 
	FOREIGN KEY(announcement_id) REFERENCES announcements (id) ON DELETE CASCADE
);

CREATE TABLE applications (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	announcement_id UUID NOT NULL, 
	applicant_id UUID NOT NULL, 
	message TEXT, 
	status VARCHAR(10) DEFAULT 'pending' NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT check_application_status CHECK (status IN ('pending', 'accepted', 'rejected')), 
	CONSTRAINT uq_applications_announcement_owner UNIQUE (announcement_id, applicant_id), 
	FOREIGN KEY(announcement_id) REFERENCES announcements (id) ON DELETE CASCADE, 
	FOREIGN KEY(applicant_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE bad_habits (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	profile_id UUID NOT NULL, 
	smoking BOOLEAN DEFAULT FALSE NOT NULL, 
	pets BOOLEAN DEFAULT FALSE NOT NULL, 
	sleep_mode VARCHAR(10) DEFAULT 'early' NOT NULL, 
	noise_preference VARCHAR(10) DEFAULT 'quiet' NOT NULL, 
	guests BOOLEAN DEFAULT FALSE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT check_sleep_mode CHECK (sleep_mode IN ('early', 'late')), 
	CONSTRAINT check_bad_habits_noise CHECK (noise_preference IN ('quiet', 'loud')), 
	UNIQUE (profile_id), 
	FOREIGN KEY(profile_id) REFERENCES profiles (id) ON DELETE CASCADE
);

CREATE TABLE chats (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	match_id UUID NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (match_id), 
	FOREIGN KEY(match_id) REFERENCES matches (id) ON DELETE CASCADE
);

CREATE TABLE hobbies (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	profile_id UUID NOT NULL, 
	films BOOLEAN DEFAULT FALSE NOT NULL, 
	music BOOLEAN DEFAULT FALSE NOT NULL, 
	sports BOOLEAN DEFAULT FALSE NOT NULL, 
	reading BOOLEAN DEFAULT FALSE NOT NULL, 
	gaming BOOLEAN DEFAULT FALSE NOT NULL, 
	books BOOLEAN DEFAULT FALSE NOT NULL, 
	photography BOOLEAN DEFAULT FALSE NOT NULL, 
	cooking BOOLEAN DEFAULT FALSE NOT NULL, 
	arts BOOLEAN DEFAULT FALSE NOT NULL, 
	table_games BOOLEAN DEFAULT FALSE NOT NULL, 
	travel BOOLEAN DEFAULT FALSE NOT NULL, 
	walking BOOLEAN DEFAULT FALSE NOT NULL, 
	dancing BOOLEAN DEFAULT FALSE NOT NULL, 
	singing BOOLEAN DEFAULT FALSE NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (profile_id), 
	FOREIGN KEY(profile_id) REFERENCES profiles (id) ON DELETE CASCADE
);

CREATE TABLE preferences (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	profile_id UUID NOT NULL, 
	age_min INTEGER NOT NULL, 
	age_max INTEGER NOT NULL, 
	gender_preference VARCHAR(10) NOT NULL, 
	budget_max INTEGER NOT NULL, 
	city_preference VARCHAR(100) NOT NULL, 
	district_preference TEXT[] NOT NULL, 
	metro_preference TEXT[] NOT NULL, 
	date_preference DATE DEFAULT CURRENT_DATE NOT NULL, 
	smoking_preference VARCHAR(10) DEFAULT 'any' NOT NULL, 
	pets_preference VARCHAR(10) DEFAULT 'any' NOT NULL, 
	guests_preference VARCHAR(10) DEFAULT 'any' NOT NULL, 
	sleep_mode_preference VARCHAR(10) DEFAULT 'any' NOT NULL, 
	noise_preference VARCHAR(10) DEFAULT 'any' NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT check_age_min CHECK (age_min >= 18 AND age_min <= 99), 
	CONSTRAINT check_age_max CHECK (age_max >= 18 AND age_max <= 99), 
	CONSTRAINT check_age_range CHECK (age_min <= age_max), 
	CONSTRAINT check_gender_pref CHECK (gender_preference IN ('male', 'female', 'any')), 
	CONSTRAINT check_budget CHECK (budget_max >= 0), 
	CONSTRAINT check_smoking_pref CHECK (smoking_preference IN ('any', 'yes', 'no')), 
	CONSTRAINT check_pets_pref CHECK (pets_preference IN ('any', 'yes', 'no')), 
	CONSTRAINT check_guests_pref CHECK (guests_preference IN ('any', 'yes', 'no')), 
	CONSTRAINT check_sleep_pref CHECK (sleep_mode_preference IN ('any', 'early', 'late')), 
	CONSTRAINT check_pref_noise CHECK (noise_preference IN ('any', 'quiet', 'loud')), 
	UNIQUE (profile_id), 
	FOREIGN KEY(profile_id) REFERENCES profiles (id) ON DELETE CASCADE
);

CREATE TABLE messages (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	chat_id UUID NOT NULL, 
	sender_id UUID NOT NULL, 
	content TEXT NOT NULL, 
	sent_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	is_read BOOLEAN DEFAULT FALSE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT check_message_content CHECK (length(trim(content)) > 0), 
	FOREIGN KEY(chat_id) REFERENCES chats (id) ON DELETE CASCADE, 
	FOREIGN KEY(sender_id) REFERENCES users (id) ON DELETE CASCADE
);
