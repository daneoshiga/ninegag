import html
from tortoise.models import Model
from tortoise import fields


class Post(Model):
    id = fields.CharField(max_length=8, pk=True)
    url = fields.CharField(max_length=128)
    file_url = fields.CharField(max_length=128)
    title = fields.CharField(max_length=128)
    section = fields.ForeignKeyField('models.Section', related_name='posts')
    post_type = fields.CharField(max_length=16)
    has_audio = fields.BooleanField()
    tags = fields.CharField(max_length=255)

    async def caption(self):
        await self.fetch_related('section')
        caption = ("<a href='{p.url}'>{p.title}</a>\n\n"
                   "#{p.section.name}".format(p=self))

        if self.tags:
            caption = caption + ' ' + ' '.join("#{tag}".format(
                tag=tag.replace('-', '_')) for tag in self.tags.split(','))

        caption = html.unescape(caption)
        return caption

    def is_photo(self):
        return self.post_type == "Photo"

    def is_video(self):
        return self.post_type == "Animated" and self.has_audio

    def is_gif(self):
        return self.post_type == "Animated" and not self.has_audio


class Section(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=32)