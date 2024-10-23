var LineReader = function (options) {

    if (!(this instanceof LineReader)) {
        return new LineReader(options);
    }

    var internals = this._internals = {};
    var self = this;

    internals.reader = new FileReader();

    internals.chunkSize = (options && options.chunkSize) ? options.chunkSize : 1024;

    /**
     * 让我们创建一个对象来让用户定义的事件回调
     */
    internals.events = {};

    /**
     * 'canRead' 将被设置为false，如果在的FileReader＃中止方法被触发
     */
    internals.canRead = true;

    internals.reader.onload = function () {

        internals.chunk += this.result;

        /**
         *如果处理的文本包含一个换行符
         */
        if (/\r|\n/.test(internals.chunk)) {
            /**
             * 拆分文本行的数组
             */
            internals.lines = internals.chunk.match(/[^\r\n]+/g);

            /**
             *如果仍有更多的数据读取，保存最后一行，因为它可能是不完整的
             */
            if (self._hasMoreData()) {
                /**
                 * 如果装入块以\n换行符结束，最后一行是完整的，我们并不需要存储它
                 */
                internals.chunk = internals.chunk[internals.chunk.length - 1] === '\n' ?
                    '' :
                    internals.lines.pop();
            }

            self._step();

            /**
             *如果文本不包含换行符
             */
        } else {

            /**
             * 启动新一轮的读取过程，如果还有读取数据
             */
            if (self._hasMoreData()) {
                return self.read();
            }

            /**
             * 如果没有数据剩下被读取，但仍然有存储在“块”的数据，发出它作为一行
             */
            if (internals.chunk.length) {
                return self._emit('line', [
                    internals.chunk,
                    self._emit.bind(self, 'end')
                ]);
            }

            /**
             * 如果没有存储在“块”的数据，发出结束事件
             */
            self._emit('end');
        }
    };


    internals.reader.onerror = function () {
        /**
         * 发出错误事件，沿着错误对象给回调传递“这”指针“的FileReader”实例
         */
        self._emit('error', [this.error]);
    };
};


/**
 *事件绑定
* @eventName- 绑定到事件的名称
* @ - 当事件触发执行函数
 */
LineReader.prototype.on = function (eventName, cb) {
    this._internals.events[eventName] = cb;
};


LineReader.prototype.read = function (file) {
    var internals = this._internals;

    /**
     * 如果“文件”是定义有效的，那么我们希望得到一些关于它的信息和重置 'readPos', 'chunk', and 'lines'
     */
    if (typeof file !== 'undefined') {
        internals.file = file;
        internals.fileLength = file.size;
        internals.readPos = 0;
        internals.chunk = '';
        internals.lines = [];
    }

    /**
     * 提取该文件的部分用于阅读开始 'readPos' and 结束于 'readPos + chunkSize'
     */
    var blob = internals.file.slice(internals.readPos, internals.readPos + internals.chunkSize);

    /**
     * 更新当前读取位置
     */
    internals.readPos += internals.chunkSize;

    /**
     * 阅读blob 作为 文本
     */
    internals.reader.readAsText(blob, "UTF-8");
};


/**
 * 停止读取过程
 */
LineReader.prototype.abort = function () {
    this._internals.canRead = false;
};


/**
 * LineReader#_step
 *
 * Internal:获取下一行并发送它作为一个`line`事件
 */
LineReader.prototype._step = function () {
    var internals = this._internals;

    /**
     * 如果没有行剩下发送，但仍有数据剩下被读取，
   *再次启动读进程，否则发送“结束”事件
     */
    if (internals.lines.length === 0) {
        if (this._hasMoreData()) {
            return this.read();
        }
        return this._emit('end');
    }

    /**
     * 如果读数进程尚未终止，发送的第一元素在行数组，并在用户通过_step“ 准备调用下一行。我们必须绑定“_step'到'this'，
      *否则这将是在错误的范围内调用它
     */
    if (internals.canRead) {
        this._emit('line', [
            internals.lines.shift(),
            this._step.bind(this)
        ]);
    } else {
        /**
         *如果我们不能读，发出“结束”事件
         */
        this._emit('end');
    }
};


/**
 * Internal: 确定是否还有更多的数据读取。
 */
LineReader.prototype._hasMoreData = function () {
    var internals = this._internals;
    return internals.readPos <= internals.fileLength;
};

/**
 *处理事件的发送
* @ - 发生事件的名称
* @ - 参数数组来发送到事件回调函数
 */
LineReader.prototype._emit = function (event, args) {
    var boundEvents = this._internals.events;

    /**
     * 如果用户已经绑定请求事件
     */
    if (typeof boundEvents[event] === 'function') {
        /**
         * Use apply to ensure correct scope, and pass in the 'args' array to
         * be used as arguments for the callback 使用apply确保正确的范围，传递'args'数组作参数用于为回调
         */
        boundEvents[event].apply(this, args);
    }
};
