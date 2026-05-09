import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  // Create Story: Chapter 1
  const story = await prisma.story.create({
    data: {
      id: 'story_01',
      title: 'Субботнее утро в твоём городе',
      description: 'Одно утро, которое может всё изменить. Кафе, prosecco, галерея и закрытая дверь.',
      chapter: 1,
      published: true,
    },
  });

  // Scene 0: Character creation
  await prisma.scene.create({
    data: {
      sceneId: 'scene_00_heroine_creation',
      storyId: story.id,
      type: 'interactive',
      textDefault: 'Привет. Это история про одно твоё субботнее утро — и о том, как оно может всё изменить.\n\nДавай познакомимся. Как тебя зовут?',
      illustrationPrompt: 'Cozy bedroom, morning light through curtains, soft focus, warm tones, feminine atmosphere',
      choices: {
        create: [
          { choiceId: 'choice_00_name', text: 'Ввести имя...', effects: {}, nextSceneId: 'scene_01_morning_wake' },
        ],
      },
    },
  });

  // Scene 1: Morning wake
  await prisma.scene.create({
    data: {
      sceneId: 'scene_01_morning_wake',
      storyId: story.id,
      type: 'interactive',
      location: 'Спальня',
      time: '08:30',
      textDefault: 'Субботнее утро. Сквозь полуприоткрытые шторы пробивается солнце — золотые лучи полосами ложатся на подушку. За окном шумит ветер и слышно чириканье птиц.\n\nТы просыпаешься медленно, без будильника. В комнате тепло и пахнет свежим постельным бельём. Ты решила позавтракать в кафе неподалёку.',
      textRomantic: 'Субботнее утро. Солнце заливает комнату золотым светом, и ты просыпаешься с лёгким предвкушением — суббота обещает что-то особенное. За окном птицы поют, и воздух пахнет летом.\n\nТы решаешь: сегодня — день для себя. Начнём с завтрака в том новом кафе.',
      textDominant: 'Ты просыпаешься по внутреннему распорядку — даже в субботу. Но сегодня ты сама решаешь, каким будет день.\n\nПервое решение: завтрак вне дома. Новое кафе. Новые возможности.',
      illustrationPrompt: 'Cozy bedroom morning light, female POV, sun through sheer curtains, warm golden tones, soft romantic atmosphere',
      choices: {
        create: [
          { choiceId: 'choice_01_a', text: 'Поваляться ещё 15 минут, наслаждаясь теплом', effects: { romanticism: 1, comfort: 1 }, nextSceneId: 'scene_02_choosing_outfit_cafe' },
          { choiceId: 'choice_01_b', text: 'Встать сразу — хочу успеть к открытию', effects: { dominance: 1, punctuality: 1 }, nextSceneId: 'scene_02_choosing_outfit_cafe' },
          { choiceId: 'choice_01_c', text: 'Взять телефон, проверить соцсети', effects: { curiosity: 1 }, nextSceneId: 'scene_02_choosing_outfit_cafe' },
        ],
      },
    },
  });

  // Scene 2: Choosing outfit for cafe
  await prisma.scene.create({
    data: {
      sceneId: 'scene_02_choosing_outfit_cafe',
      storyId: story.id,
      type: 'interactive',
      location: 'Гардероб',
      time: '09:00',
      textDefault: 'Ты стоишь перед зеркалом. Завтрак в кафе — ничего особенного, но суббота… почему бы и не нарядиться?\n\n«Нелепый наряд для завтрака в кафе неподалёку… — думаешь ты. — Но пусть будет.»',
      illustrationPrompt: 'Woman choosing outfit in front of mirror, closet with clothes, morning light, feminine bedroom, warm tones',
      choices: {
        create: [
          { choiceId: 'choice_02_a', text: 'Струящаяся юбочка миди + белая рубашка', effects: { femininity: 2, romanticism: 1 }, nextSceneId: 'scene_03_cafe_arrival' },
          { choiceId: 'choice_02_b', text: 'Джинсы + топ с открытыми плечами', effects: { casual: 1, confidence: 1 }, nextSceneId: 'scene_03_cafe_arrival' },
          { choiceId: 'choice_02_c', text: 'Платье-рубашка, слегка застёгнутое', effects: { style: 2, mystery: 1 }, nextSceneId: 'scene_03_cafe_arrival' },
        ],
      },
    },
  });

  // Scene 3: Cafe arrival
  await prisma.scene.create({
    data: {
      sceneId: 'scene_03_cafe_arrival',
      storyId: story.id,
      type: 'narrative',
      location: 'Кафе «Мокко»',
      time: '09:30',
      textDefault: 'Кафе оказалось чудом. Панорамные окна, деревянные столы, пионы на подоконниках. Воздух пахнет свежемолотым кофе и круассанами.\n\nТы садишься за столик у окна. Солнце ласково греет щёку.\n\n— Что будете заказывать? — голос был молодым, почти нежным.\n\nТы поднимаешь глаза.',
      illustrationPrompt: 'Cozy coffee shop interior, warm lighting, morning atmosphere, wooden tables, flowers on windowsill, cinematic',
      choices: {
        create: [
          { choiceId: 'choice_03_continue', text: 'Смотреть...', effects: {}, nextSceneId: 'scene_04_lesha' },
        ],
      },
    },
  });

  // Scene 4: Lesha (waiter)
  await prisma.scene.create({
    data: {
      sceneId: 'scene_04_lesha',
      storyId: story.id,
      type: 'interactive',
      location: 'Кафе «Мокко»',
      time: '09:32',
      textDefault: 'Перед тобой стоит парень. Лет двадцать, не больше. Симпатичный — прямолинейная челюсть, веснушки на носу, взгляд хитроватый.\n\nНа шее виднеется татуировка — тонкая линия, уходящая под ключицу. Ты успеваешь разглядеть завиток — похоже, ветвь папоротника.\n\n— Круассан с миндалём и латте, — говоришь ты.\n— Лавандовый сироп добавить? — улыбается он кривовато. — У нас новый.',
      illustrationPrompt: 'Young handsome waiter, 20 years old, freckles, tattoo on neck, coffee shop, warm lighting, friendly smile',
      choices: {
        create: [
          { choiceId: 'choice_04_a', text: 'Сделать вид, что не заметила татуировку', effects: { restraint: 1, mystery: 1 }, nextSceneId: 'scene_05_prosecco' },
          { choiceId: 'choice_04_b', text: 'Улыбнуться, глядя на татуировку', effects: { flirt: 1 }, nextSceneId: 'scene_05_prosecco' },
          { choiceId: 'choice_04_c', text: '«Что за тату?»', effects: { boldness: 2, flirt: 1 }, nextSceneId: 'scene_05_prosecco' },
        ],
      },
    },
  });

  // Scene 5: Prosecco
  await prisma.scene.create({
    data: {
      sceneId: 'scene_05_prosecco',
      storyId: story.id,
      type: 'interactive',
      location: 'Кафе «Мокко»',
      time: '09:45',
      textDefault: 'Через десять минут он возвращается. В руке у него не счёт, а бокал.\n\n— Prosecco. От заведения. Для самой красивой гостьи этого утра.\n\nОн ставит его перед тобой с лёгкой ухмылкой и отходит, не дожидаясь ответа.',
      illustrationPrompt: 'Glass of prosecco on wooden table, golden bubbles, coffee shop background, warm morning light, soft focus',
      choices: {
        create: [
          { choiceId: 'choice_05_a', text: '«Слишком рано?» — но взять бокал', effects: { playful: 1, flirt: 1 }, nextSceneId: 'scene_06_phone_number' },
          { choiceId: 'choice_05_b', text: 'Сказать спасибо, улыбнуться и отпить молча', effects: { mystery: 2, sensuality: 1 }, nextSceneId: 'scene_06_phone_number' },
          { choiceId: 'choice_05_c', text: '«Часто так радуете гостей?»', effects: { playful: 2, confidence: 1 }, nextSceneId: 'scene_06_phone_number' },
        ],
      },
    },
  });

  // Scene 6: Phone number
  await prisma.scene.create({
    data: {
      sceneId: 'scene_06_phone_number',
      storyId: story.id,
      type: 'interactive',
      location: 'Кафе «Мокко»',
      time: '10:15',
      textDefault: 'Когда пришло время уходить, он принёс счёт. Но вместе со счётом — маленькую салфетку с номером телефона. И сердцем нарисованным рядом.\n\n— На чай можно оставить по номеру телефона, — сказал он, не глядя. — Мой номер. На случай, если захочешь… пообщаться позже.',
      illustrationPrompt: 'Small napkin with handwritten phone number and heart, coffee shop table, soft warm light, intimate moment',
      choices: {
        create: [
          { choiceId: 'choice_06_a', text: 'Спрятать салфетку в сумочку', effects: { mystery: 1, confidence: 1 }, nextSceneId: 'scene_07_choosing_outfit_gallery' },
          { choiceId: 'choice_06_b', text: 'Посмотреть ему вслед и подмигнуть', effects: { flirt: 2 }, nextSceneId: 'scene_07_choosing_outfit_gallery' },
          { choiceId: 'choice_06_c', text: 'Переписать номер, оставить салфетку', effects: { restraint: 1, strategy: 1 }, nextSceneId: 'scene_07_choosing_outfit_gallery' },
        ],
      },
    },
  });

  // Scene 7: Choosing outfit for gallery
  await prisma.scene.create({
    data: {
      sceneId: 'scene_07_choosing_outfit_gallery',
      storyId: story.id,
      type: 'interactive',
      location: 'Гардероб',
      time: '11:00',
      textDefault: 'Ты вернулась домой. Сегодня в планах — выставка в галерее «Арт-Пространство».\n\nТы стоишь перед шкафом: во что одеться? Это всё-таки галерея...',
      illustrationPrompt: 'Woman choosing dress for evening, closet with elegant clothes, mirror reflection, warm bedroom light',
      choices: {
        create: [
          { choiceId: 'choice_07_a', text: 'Платье-карандаш (чёрное/бордовое/зелёное)', effects: { elegance: 2, sensuality: 1 }, nextSceneId: 'scene_08_choosing_lingerie' },
          { choiceId: 'choice_07_b', text: 'Кожаная юбка + шёлковая блузка', effects: { sensuality: 3, boldness: 2 }, nextSceneId: 'scene_08_choosing_lingerie' },
        ],
      },
    },
  });

  // Scene 8: Choosing lingerie (KEY SCENE)
  await prisma.scene.create({
    data: {
      sceneId: 'scene_08_choosing_lingerie',
      storyId: story.id,
      type: 'interactive',
      location: 'Спальня',
      time: '11:20',
      textDefault: 'Наряд выбран. Но прежде чем его надеть, ты открываешь нижний ящик комода. Тот самый, который открываешь редко.\n\nТам лежит ОН — комплект, который ты купила давно, но так и не решилась надеть. Он кажется очень откровенным.\n\n«Чёртов \'шлюший\' комплект», — шепчешь ты, но улыбаешься.',
      textDominant: 'Наряд выбран. Но ты знаешь: сегодня особенный день. Открываешь нижний ящик — тот, что для особых случаев.\n\nКомплект ждёт. Он создан для того, чтобы чувствовать себя сильной. Смелой. Неостановимой.\n\n«Сегодня я никому ничего не должна», — думаешь ты.',
      illustrationPrompt: 'Elegant lingerie set on bed, black lace, stockings, garter belt, soft morning light, feminine, sensual atmosphere',
      choices: {
        create: [
          { choiceId: 'choice_08_a', text: '«Noir» — чёрный кружевной набор с чулками', effects: { mystery: 2, sensuality: 2 }, nextSceneId: 'scene_09_gallery_arrival', condition: { flag: 'lingerie_black_set' } },
          { choiceId: 'choice_08_b', text: '«Bordeaux» — бордовый комплект', effects: { sensuality: 3, passion: 2 }, nextSceneId: 'scene_09_gallery_arrival', condition: { flag: 'lingerie_burgundy_set' } },
          { choiceId: 'choice_08_c', text: '«Nude Secret» — телесный с чёрным кружевом', effects: { sensuality: 2, confidence: 3 }, nextSceneId: 'scene_09_gallery_arrival', condition: { flag: 'lingerie_nude_set' } },
        ],
      },
    },
  });

  // Scene 9: Gallery arrival
  await prisma.scene.create({
    data: {
      sceneId: 'scene_09_gallery_arrival',
      storyId: story.id,
      type: 'narrative',
      location: 'Галерея «Арт-Пространство»',
      time: '12:30',
      textDefault: 'Галерея прекрасна. Белые стены, высокие потолки, по которым пляшут лучи солнца. В воздухе — лёгкий запах лака и краски.\n\nВыставка «Чувственные геометрии» — абстракция, телесность, линии, которые будоражат воображение.\n\nНо ты замечаешь его ещё во втором зале.',
      illustrationPrompt: 'Modern art gallery interior, white walls, abstract paintings, natural light, elegant visitors, minimalist architecture',
      choices: {
        create: [
          { choiceId: 'choice_09_continue', text: 'Посмотреть...', effects: {}, nextSceneId: 'scene_10_first_glance' },
        ],
      },
    },
  });

  // Scene 10: First glance at Max
  await prisma.scene.create({
    data: {
      sceneId: 'scene_10_first_glance',
      storyId: story.id,
      type: 'interactive',
      location: 'Зал 2, галерея',
      time: '13:00',
      textDefault: 'Он стоит у полотна — спиной к тебе. Тесный костюм, белая рубашка с расстёгнутыми пуговицами. Пиджак перекинут через предплечье.\n\nПотом он оборачивается.\n\nЗелёные глаза. Лёгкая щетина. Взгляд скользит по тебе — быстро, но на секунду задерживается.',
      illustrationPrompt: 'Handsome man in fitted suit, white shirt slightly unbuttoned, green eyes, art gallery background, holding jacket, confident pose',
      choices: {
        create: [
          { choiceId: 'choice_10_a', text: 'Посмотреть на него прямо, не отводя глаз', effects: { confidence: 1, connection: 1 }, nextSceneId: 'scene_11_gallery_exploration' },
          { choiceId: 'choice_10_b', text: 'Сделать вид, что рассматриваешь картину', effects: { mystery: 1, anticipation: 1 }, nextSceneId: 'scene_11_gallery_exploration' },
          { choiceId: 'choice_10_c', text: 'Пройти мимо, оставив шлейф духов', effects: { sensuality: 2, seduction: 1 }, nextSceneId: 'scene_11_gallery_exploration' },
        ],
      },
    },
  });

  // Scene 11: Gallery exploration
  await prisma.scene.create({
    data: {
      sceneId: 'scene_11_gallery_exploration',
      storyId: story.id,
      type: 'narrative',
      location: 'Галерея',
      time: '13:15',
      textDefault: 'Ты продолжаешь осматривать выставку, но внимание раздвоено. Каждый раз, входя в новый зал, ты непроизвольно ищешь его взглядом.\n\nВ четвёртом зале вас остаётся двое. Ты стоишь перед полотном — сплетение тел — и чувствуешь его запах. Древесные ноты, кедр, что-то тёплое. Он стоит позади. В двух шагах.',
      illustrationPrompt: 'Woman viewing abstract painting in gallery, silhouette of man behind her, soft gallery lighting, intimate atmosphere',
      choices: {
        create: [
          { choiceId: 'choice_11_continue', text: '...', effects: {}, nextSceneId: 'scene_12_the_encounter' },
        ],
      },
    },
  });

  // Scene 12: The encounter
  await prisma.scene.create({
    data: {
      sceneId: 'scene_12_the_encounter',
      storyId: story.id,
      type: 'interactive',
      location: 'Зал 4',
      time: '13:50',
      textDefault: 'Ты пошатываешься. В эти шпильки непросто стоять долго.\n\nИ в долю секунды — он позади. Его рука подхватывает тебя под локоть, твоя спина упирается в его грудь — корявую, твёрдую. Твоё бедро касается его бедра.\n\n— Всё в порядке? — голос у самого уха, низкий, почти шёпот.\n\nСердце колотится так, что, кажется, он тоже слышит.',
      illustrationPrompt: 'Man catching woman in art gallery, intimate moment, close embrace, soft lighting, romantic tension',
      choices: {
        create: [
          { choiceId: 'choice_12_a', text: 'Обернуться к нему лицом', effects: { intimacy: 2, passion: 1 }, nextSceneId: 'scene_13_last_hall' },
          { choiceId: 'choice_12_b', text: 'Слегка отстраниться', effects: { mystery: 1, flirt: 1 }, nextSceneId: 'scene_13_last_hall' },
          { choiceId: 'choice_12_c', text: 'Посмотреть в глаза и промолчать', effects: { sensuality: 3, tension: 1 }, nextSceneId: 'scene_13_last_hall' },
        ],
      },
    },
  });

  // Scene 13: Last hall (the closed room)
  await prisma.scene.create({
    data: {
      sceneId: 'scene_13_last_hall',
      storyId: story.id,
      type: 'narrative',
      location: 'Закрытый зал',
      time: '14:00',
      textDefault: '— Здесь некуда присесть, — говорит он. — Пойдёмте.\n\nОн ведёт тебя к дальнему концу коридора. Там двери, прикрытые красной бархатной лентой: «Зал готовится к открытию».\n\nВнутри — полумрак. Новая мебель прикрыта целлофаном. Он скидывает плёнку с бархатного дивана и помогает тебе сесть.\n\nТы садишься. Диван оказался ниже, чем ожидала.\n\nОн оказывается прямо перед тобой. Лицом на уровне его ремня.',
      illustrationPrompt: 'Dimly lit gallery room, velvet couch, plastic sheets on furniture, intimate atmosphere, man standing before seated woman',
      choices: {
        create: [
          { choiceId: 'choice_13_continue', text: '...', effects: {}, nextSceneId: 'scene_14_on_the_couch' },
        ],
      },
    },
  });

  // Scene 14: On the couch
  await prisma.scene.create({
    data: {
      sceneId: 'scene_14_on_the_couch',
      storyId: story.id,
      type: 'interactive',
      location: 'Закрытый зал',
      time: '14:05',
      textDefault: 'Рубашка приоткрыта — ты видишь тёмный треугольник груди, лёгкий загар, ключицы.\n\n— В порядке? — спрашивает он снова. — Сердцебиение нормальное?\n\nТы поднимаешь глаза. Зелёные. Очень близко.\n\n«Он врач. Он готов помочь. А у меня мысли совсем другие…»\n\nТы оцениваешь его. Длинные пальцы, широкие плечи, щетина, которую хочется коснуться.',
      illustrationPrompt: 'Intimate scene, woman sitting on couch looking up at standing man, dim light, close distance, romantic tension',
      isPremium: true,
      choices: {
        create: [
          { choiceId: 'choice_14_a', text: 'Взять воду из его рук и отпить', effects: { sensuality: 1, intimacy: 1 }, nextSceneId: 'scene_15_the_door' },
          { choiceId: 'choice_14_b', text: '«У меня всё в порядке. Совсем»', effects: { seduction: 2, boldness: 1 }, nextSceneId: 'scene_15_the_door' },
        ],
      },
    },
  });

  // Scene 15: The door (point of no return)
  await prisma.scene.create({
    data: {
      sceneId: 'scene_15_the_door',
      storyId: story.id,
      type: 'cliffhanger',
      location: 'Закрытый зал',
      time: '14:08',
      textDefault: 'Ты встаёшь. Оперевшись на его предплечье, делаешь шаг к двери.\n\nИ останавливаешься. Разворачиваешься. Окидываешь его взглядом — снизу вверх, медленно.\n\nЗелёные. Ждущие.\n\nТы толкаешь дверь ногой. Она захлопывается.\n\nТы стоишь спиной к двери. В полумраке, среди целлофана и новой мебели, в чёртовом «шлюшем» комплекте белья, под платьем, которое сейчас будет стянуто.\n\n— Подойди, — говоришь ты.',
      textDominant: 'Ты встаёшь. Делаешь шаг к двери — и останавливаешься. Разворачиваешься. Смотришь на него сверху вниз, оценивая.\n\nОн — твой. Ты это знаешь. Он тоже.\n\nТы толкаешь дверь ногой. Она захлопывается с глухим стуком.\n\n— Подойди, — говоришь ты. Не вопрос. Приказ.',
      illustrationPrompt: 'Woman standing by closed door, back to door, facing man, dimly lit room, sensual atmosphere, dress, lingerie visible',
      isPremium: true,
      choices: {
        create: [
          { choiceId: 'choice_15_a', text: 'Начать с его рубашки', effects: { boldness: 2, sensuality: 2 }, nextSceneId: 'scene_16_behind_doors_a', condition: { stat: { name: 'boldness', min: 3 } } },
          { choiceId: 'choice_15_b', text: 'Дать ему вести', effects: { intimacy: 2, sensuality: 2 }, nextSceneId: 'scene_16_behind_doors_b', condition: { stat: { name: 'romanticism', min: 3 } } },
        ],
      },
    },
  });

  // Scene 16A: Behind doors - Bold path
  await prisma.scene.create({
    data: {
      sceneId: 'scene_16_behind_doors_a',
      storyId: story.id,
      type: 'narrative',
      location: 'Закрытый зал',
      time: '14:10',
      textDefault: 'Ты начинаешь с его рубашки. Пуговицы одну за другой — медленно. Щетина колется. Поцелуй — сначала уголок рта, потом полноценно, с языком, с тем вкусом, который ты запомнишь.\n\nРубашка спадает на пол.\n\nТы опускаешь взгляд. Ремень — прямо перед тобой. Пальцы находят пряжку, щёлкают. Ты опускаешься на колени на мягкий ковёр.\n\n«Этот комплект…» — шепчет он. — «Ты планировала это?»\n\nТы не отвечаешь. Улыбаешься с закрытыми глазами.',
      illustrationPrompt: 'Intimate moment, woman unbuttoning man shirt, dim light, passionate kiss, soft shadows, sensual atmosphere, elegant',
      isPremium: true,
      choices: {
        create: [
          { choiceId: 'choice_16a_a', text: 'Сверху (контролировать)', effects: { dominance: 3, sensuality: 3 }, nextSceneId: 'scene_17_afterglow' },
          { choiceId: 'choice_16a_b', text: 'Сзади (отдаться)', effects: { submission: 2, sensuality: 3 }, nextSceneId: 'scene_17_afterglow' },
        ],
      },
    },
  });

  // Scene 16B: Behind doors - Romantic path
  await prisma.scene.create({
    data: {
      sceneId: 'scene_16_behind_doors_b',
      storyId: story.id,
      type: 'narrative',
      location: 'Закрытый зал',
      time: '14:10',
      textDefault: 'Он не даёт тебе опуститься. Руки поднимают платье — медленно, по бёдрам.\n\n— Чёрт, — выдыхает он, увидев комплект.\n\nПодхватывает тебя под ягодицы — легко, с силой — и поднимает на руки. Ноги обвивают его талию, спина прижимается к двери, и он входит в тебя.\n\n— Дверь, — тихо смеёшься ты.\n— Пусть скрипит, — отвечает он в твою шею.',
      illustrationPrompt: 'Passionate embrace, man lifting woman against door, intimate moment, dim gallery light, romantic intensity',
      isPremium: true,
      choices: {
        create: [
          { choiceId: 'choice_16b_continue', text: '...', effects: { intimacy: 3, sensuality: 3 }, nextSceneId: 'scene_17_afterglow' },
        ],
      },
    },
  });

  // Scene 17: Afterglow
  await prisma.scene.create({
    data: {
      sceneId: 'scene_17_afterglow',
      storyId: story.id,
      type: 'narrative',
      location: 'Закрытый зал',
      time: '14:35',
      textDefault: 'Потом — тишина. Тяжёлое дыхание. Запах пота и духов.\n\nТы лежишь на диване, он — рядом, обнимая за талию.\n\n— Я Макс, — говорит он.\n— {heroine_name}, — отвечаешь ты.\n\n— Я не врач. Я искусствовед.\n\nТы смеёшься в его плечо.\n— А я не чуть не упала. Я притворялась.\n\nОн откидывает голову и смеётся — громко, по-настоящему.\n\n— Твои трусики. Куда они делись?\n— Ты их сорвал и положил в карман пиджака.\n\nПауза.\n\n— Приедешь за ними?',
      illustrationPrompt: 'Couple lying on couch after intimacy, soft dim light, content expressions, intimate postlude, gallery room',
      choices: {
        create: [
          { choiceId: 'choice_17_a', text: '«Сама приеду. И заберу. И, может, что-то ещё…»', effects: { seduction: 2 }, nextSceneId: 'scene_18_taxi' },
          { choiceId: 'choice_17_b', text: '«Зависит от того, что ты покажешь в следующий раз»', effects: { mystery: 2 }, nextSceneId: 'scene_18_taxi' },
        ],
      },
    },
  });

  // Scene 18: Taxi
  await prisma.scene.create({
    data: {
      sceneId: 'scene_18_taxi',
      storyId: story.id,
      type: 'cliffhanger',
      location: 'Такси',
      time: '15:30',
      textDefault: 'Ты едешь домой. За окном — город, залитый вечерним солнцем.\n\nТы вспоминаешь рубашку на полу. Зелёные глаза. Его руки на твоей талии.\n\nИ понимаешь: на тебе нет трусиков.\n\n«Чертов \'шлюший\' комплект», — думаешь ты, чувствуя, как щёки горят. — «И я бы надела его снова».\n\nТелефон вибрирует.\n\n**Макс:** «Зал открылся. Первый посетитель — пожилая пара. Они не знают, что произошло на их диване. P.S. Твои… ждут хозяйку.»\n\n**Лёша:** «Привет. Это Лёша из кафе. Надеюсь, prosecco не был слишком рано. Я сегодня до 22:00.»\n\nДва мужчины. Два мира. Твой выбор.',
      illustrationPrompt: 'Woman in taxi at dusk, city lights through window, thoughtful smile, holding phone, golden hour, urban atmosphere',
      choices: {
        create: [
          { choiceId: 'choice_18_a', text: 'Ответить Максу → Глава 2: Вечер у Макса', effects: { max_relationship: 20 }, nextSceneId: 'scene_ch2_01' },
          { choiceId: 'choice_18_b', text: 'Ответить Лёше → Глава 3: Ночь с Лёшей', effects: { lesha_relationship: 20 }, nextSceneId: 'scene_ch3_01' },
          { choiceId: 'choice_18_c', text: 'Ответить обоим → Рискованно!', effects: { boldness: 2 }, nextSceneId: 'scene_ch2_01' },
        ],
      },
    },
  });

  console.log('✅ Seed completed: Story "Субботнее утро" with 18 scenes and 35 choices');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
